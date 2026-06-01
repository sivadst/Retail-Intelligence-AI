"""Demand forecasting with Prophet."""
import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from prophet import Prophet
import pandas as pd
import json

from app.models import Dataset
from app.core import NotFoundException

logger = logging.getLogger(__name__)


class ForecastingService:
    """Demand forecasting service using Prophet."""

    @staticmethod
    def _detect_date_column(schema: dict) -> Optional[str]:
        """Find date column from schema."""
        from app.services.analytics_service import AnalyticsService
        return AnalyticsService._detect_column(schema, "date")

    @staticmethod
    def _detect_metric_column(schema: dict, metric: str) -> Optional[str]:
        """Find metric column from schema."""
        from app.services.analytics_service import AnalyticsService
        return AnalyticsService._detect_column(schema, metric)

    @staticmethod
    async def generate_forecast(
        db: AsyncSession,
        dataset_id: UUID,
        metric: str = "sales",
        granularity: str = "daily",
        horizon: int = 30,
    ) -> dict:
        """Generate forecast using Prophet.
        
        Args:
            dataset_id: Dataset to forecast on
            metric: "sales", "profit", "orders"
            granularity: "daily", "weekly", "monthly"
            horizon: forecast days (30, 60, 90)
        """
        result = await db.execute(select(Dataset).where(Dataset.id == str(dataset_id)))
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise NotFoundException(f"Dataset {dataset_id} not found")

        schema = dataset.columns_schema or {}
        table_name = f"dataset_data_{dataset_id}"

        # Find columns
        date_col = ForecastingService._detect_date_column(schema)
        metric_col = ForecastingService._detect_metric_column(schema, metric)

        if not all([date_col, metric_col]):
            return {
                "error": f"Dataset missing required columns for {metric} forecasting"
            }

        try:
            # Aggregate data to granularity
            date_trunc = {
                "daily": "date",
                "weekly": "week",
                "monthly": "month",
            }.get(granularity, "date")

            # Query historical data
            query = f"""
            SELECT 
                DATE_TRUNC('{date_trunc}', {date_col})::date as ds,
                SUM({metric_col}) as y
            FROM {table_name}
            WHERE {metric_col} IS NOT NULL
            GROUP BY DATE_TRUNC('{date_trunc}', {date_col})
            ORDER BY ds ASC
            """

            exec_result = await db.execute(text(query))
            rows = exec_result.mappings().all()

            if len(rows) < 10:
                return {"error": "Insufficient historical data for forecasting (minimum 10 periods)"}

            # Convert to DataFrame
            df_data = [
                {"ds": datetime.fromisoformat(str(row["ds"])), "y": float(row["y"] or 0)}
                for row in rows
            ]
            df = pd.DataFrame(df_data)

            # Fit Prophet
            model = Prophet(
                interval_width=0.95,
                daily_seasonality=granularity == "daily",
                weekly_seasonality=granularity in ["daily", "weekly"],
                yearly_seasonality=True,
            )

            # Add custom seasonality if enough data
            if len(df) > 365:
                model.add_seasonality(name='monthly', period=30, fourier_order=5)

            model.fit(df)

            # Generate forecast
            future = model.make_future_dataframe(periods=horizon, freq='D' if granularity == 'daily' else 'M')
            forecast_df = model.predict(future)

            # Calculate trend
            trend = forecast_df[['ds', 'trend']].tail(horizon).to_dict('records')

            # Calculate metrics
            historical = df.tail(30)
            mean_y = historical['y'].mean()
            std_y = historical['y'].std()

            # MAPE calculation
            test_pred = forecast_df[forecast_df['ds'] <= df['ds'].max()]
            if len(test_pred) > 0:
                mape = (abs(test_pred['yhat'] - test_pred['y']) / test_pred['y']).mean() * 100
            else:
                mape = 0

            # Detect trend direction
            recent_trend = forecast_df['trend'].tail(horizon).mean() - forecast_df['trend'].head(10).mean()
            trend_direction = "upward" if recent_trend > 0 else "downward"

            return {
                "success": True,
                "forecast": [
                    {
                        "ds": row['ds'].isoformat() if hasattr(row['ds'], 'isoformat') else str(row['ds']),
                        "yhat": round(float(row['yhat']), 2),
                        "yhat_lower": round(float(row['yhat_lower']), 2),
                        "yhat_upper": round(float(row['yhat_upper']), 2),
                    }
                    for _, row in forecast_df.tail(horizon).iterrows()
                ],
                "historical": [
                    {
                        "ds": row['ds'].isoformat() if hasattr(row['ds'], 'isoformat') else str(row['ds']),
                        "y": round(float(row['y']), 2),
                    }
                    for _, row in df.tail(60).iterrows()
                ],
                "components": {
                    "trend": trend[-30:] if len(trend) >= 30 else trend,
                },
                "metrics": {
                    "mape": round(mape, 2),
                    "mean": round(float(mean_y), 2),
                    "std": round(float(std_y), 2),
                    "trend_direction": trend_direction,
                },
                "dataset_id": str(dataset_id),
                "metric": metric,
                "granularity": granularity,
                "forecast_date": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Forecasting error: {str(e)}")
            return {"error": f"Forecasting failed: {str(e)}"}

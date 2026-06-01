"""Anomaly detection and alert management."""
import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from sklearn.ensemble import IsolationForest
import numpy as np
import pandas as pd

from app.models import Dataset, Alert
from app.core import NotFoundException

logger = logging.getLogger(__name__)


class AlertService:
    """Alert management and anomaly detection."""

    @staticmethod
    async def detect_anomalies(
        db: AsyncSession,
        dataset_id: UUID,
        lookback_days: int = 30,
    ) -> list:
        """Detect anomalies in recent data using Isolation Forest."""
        result = await db.execute(select(Dataset).where(Dataset.id == str(dataset_id)))
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise NotFoundException(f"Dataset {dataset_id} not found")

        schema = dataset.columns_schema or {}
        table_name = f"dataset_data_{dataset_id}"

        # Detect columns
        from app.services.analytics_service import AnalyticsService
        date_col = AnalyticsService._detect_column(schema, "date")
        sales_col = AnalyticsService._detect_column(schema, "sales")
        profit_col = AnalyticsService._detect_column(schema, "profit")
        discount_col = AnalyticsService._detect_column(schema, "discount")
        qty_col = AnalyticsService._detect_column(schema, "quantity")

        if not date_col or not sales_col:
            return []

        try:
            # Query recent data
            lookback = (datetime.utcnow() - timedelta(days=lookback_days)).date()
            
            query = f"""
            SELECT 
                DATE({date_col}) as date,
                SUM({sales_col}) as sales,
                SUM({profit_col}) as profit,
                AVG({discount_col}) as discount,
                SUM({qty_col}) as quantity
            FROM {table_name}
            WHERE {date_col}::date >= '{lookback}'
            GROUP BY DATE({date_col})
            ORDER BY DATE({date_col})
            """

            exec_result = await db.execute(text(query))
            rows = exec_result.mappings().all()

            if len(rows) < 5:
                return []

            # Convert to DataFrame
            data = []
            for row in rows:
                data.append({
                    "date": row["date"],
                    "sales": float(row["sales"] or 0),
                    "profit": float(row["profit"] or 0),
                    "discount": float(row["discount"] or 0),
                    "quantity": float(row["quantity"] or 0),
                })

            df = pd.DataFrame(data)

            # Prepare features for anomaly detection
            features = df[["sales", "profit", "quantity"]].fillna(0)

            if len(features) < 5:
                return []

            # Fit Isolation Forest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            anomaly_scores = iso_forest.fit_predict(features)
            anomaly_probs = iso_forest.score_samples(features)

            # Find anomalies
            anomalies = []
            for i, (is_anomaly, score) in enumerate(zip(anomaly_scores, anomaly_probs)):
                if is_anomaly == -1:  # Anomaly detected
                    row = df.iloc[i]
                    
                    # Calculate expected range from historical data
                    historical_sales = df["sales"][:-7].values if len(df) > 7 else df["sales"].values
                    expected_sales_mean = float(np.mean(historical_sales))
                    expected_sales_std = float(np.std(historical_sales))

                    anomalies.append({
                        "date": str(row["date"]),
                        "anomaly_score": round(float(score), 3),
                        "severity": "high" if score < -0.5 else "medium",
                        "affected_metrics": ["sales", "profit", "quantity"],
                        "expected_range": {
                            "sales": [
                                round(expected_sales_mean - expected_sales_std, 2),
                                round(expected_sales_mean + expected_sales_std, 2),
                            ],
                            "profit": [0, 0],  # Would calculate similarly
                        },
                        "actual_values": {
                            "sales": round(row["sales"], 2),
                            "profit": round(row["profit"], 2),
                            "quantity": round(row["quantity"], 2),
                        },
                        "explanation": f"Anomalous pattern detected: sales {row['sales']:.0f} (expected ~{expected_sales_mean:.0f})",
                    })

            return anomalies

        except Exception as e:
            logger.error(f"Anomaly detection error: {str(e)}")
            return []

    @staticmethod
    async def evaluate_alert(
        db: AsyncSession,
        alert: Alert,
        dataset_id: UUID,
    ) -> dict:
        """Evaluate if alert should trigger."""
        schema_result = await db.execute(
            select(Dataset).where(Dataset.id == str(dataset_id))
        )
        dataset = schema_result.scalar_one_or_none()
        if not dataset:
            return {"triggered": False, "reason": "Dataset not found"}

        schema = dataset.columns_schema or {}
        table_name = f"dataset_data_{dataset_id}"

        condition = alert.condition or {}
        condition_type = condition.get("type", "threshold")

        try:
            if condition_type == "threshold":
                return await AlertService._eval_threshold(
                    db, table_name, schema, condition
                )
            elif condition_type == "percent_change":
                return await AlertService._eval_percent_change(
                    db, table_name, schema, condition
                )
            elif condition_type == "anomaly":
                anomalies = await AlertService.detect_anomalies(db, dataset_id)
                return {
                    "triggered": len(anomalies) > 0,
                    "reason": f"Found {len(anomalies)} anomalies",
                    "data": anomalies,
                }
            else:
                return {"triggered": False, "reason": "Unknown condition type"}

        except Exception as e:
            logger.error(f"Alert evaluation error: {str(e)}")
            return {"triggered": False, "reason": f"Error: {str(e)}"}

    @staticmethod
    async def _eval_threshold(db, table_name, schema, condition) -> dict:
        """Evaluate threshold condition."""
        from app.services.analytics_service import AnalyticsService

        metric = condition.get("metric", "sales")
        operator = condition.get("operator", ">")
        threshold = condition.get("threshold", 0)

        metric_col = AnalyticsService._detect_column(schema, metric)
        if not metric_col:
            return {"triggered": False, "reason": f"Column {metric} not found"}

        query = f"SELECT SUM({metric_col}) as value FROM {table_name}"
        result = await db.execute(text(query))
        row = result.mappings().first()
        value = float(row["value"] or 0) if row else 0

        triggered = False
        if operator == ">":
            triggered = value > threshold
        elif operator == "<":
            triggered = value < threshold
        elif operator == ">=":
            triggered = value >= threshold
        elif operator == "<=":
            triggered = value <= threshold

        return {
            "triggered": triggered,
            "reason": f"{metric}={value:.2f} {operator} {threshold}",
            "value": value,
        }

    @staticmethod
    async def _eval_percent_change(db, table_name, schema, condition) -> dict:
        """Evaluate percent change condition."""
        from app.services.analytics_service import AnalyticsService

        metric = condition.get("metric", "sales")
        period = condition.get("period", "7d")
        threshold_pct = condition.get("threshold", -20)

        metric_col = AnalyticsService._detect_column(schema, metric)
        date_col = AnalyticsService._detect_column(schema, "date")

        if not all([metric_col, date_col]):
            return {"triggered": False, "reason": "Missing required columns"}

        # Calculate periods
        if period == "7d":
            period_days = 7
        elif period == "30d":
            period_days = 30
        else:
            period_days = 7

        today = datetime.utcnow().date()
        current_start = today - timedelta(days=period_days)
        prev_start = current_start - timedelta(days=period_days)

        query = f"""
        SELECT 
            SUM(CASE WHEN {date_col}::date >= '{current_start}' THEN {metric_col} ELSE 0 END) as current,
            SUM(CASE WHEN {date_col}::date >= '{prev_start}' AND {date_col}::date < '{current_start}' THEN {metric_col} ELSE 0 END) as previous
        FROM {table_name}
        """

        result = await db.execute(text(query))
        row = result.mappings().first()

        current = float(row["current"] or 0) if row else 0
        previous = float(row["previous"] or 1)

        pct_change = ((current - previous) / previous * 100) if previous > 0 else 0

        triggered = pct_change < threshold_pct

        return {
            "triggered": triggered,
            "reason": f"{metric} changed {pct_change:.1f}% vs {threshold_pct:.1f}% threshold",
            "pct_change": round(pct_change, 2),
        }

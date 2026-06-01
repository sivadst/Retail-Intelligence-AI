"""Real analytics engine with SQL generation and KPI calculation."""
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from difflib import get_close_matches
import statistics

from app.models import Dataset
from app.core import NotFoundException

logger = logging.getLogger(__name__)

# Column name aliases for fuzzy matching
COLUMN_ALIASES = {
    "sales": ["sales", "revenue", "total_sales", "sales_amount", "amount"],
    "profit": ["profit", "net_profit", "total_profit"],
    "date": ["order_date", "date", "transaction_date", "created_at"],
    "category": ["category", "product_category", "category_name"],
    "region": ["region", "state", "area", "territory"],
    "product": ["product_name", "product", "item", "item_name"],
    "quantity": ["quantity", "qty", "units"],
    "discount": ["discount", "discount_pct", "discount_percent"],
}


class AnalyticsService:
    """Service for computing analytics on datasets."""

    @staticmethod
    def _detect_column(schema: dict, target: str) -> Optional[str]:
        """Fuzzy match column name from schema against target."""
        if not schema or not schema.get("columns"):
            return None

        columns = list(schema["columns"].keys())
        aliases = COLUMN_ALIASES.get(target.lower(), [target.lower()])

        for alias in aliases:
            matches = get_close_matches(alias, columns, n=1, cutoff=0.6)
            if matches:
                return matches[0]
        return None

    @staticmethod
    def _get_date_filter(date_range: str, date_col: str) -> tuple[str, dict]:
        """Generate WHERE clause for date filtering.
        
        Returns: (where_clause, params)
        """
        now = datetime.utcnow()
        params = {}

        if date_range == "last_7d":
            start = now - timedelta(days=7)
        elif date_range == "last_30d":
            start = now - timedelta(days=30)
        elif date_range == "last_90d":
            start = now - timedelta(days=90)
        elif date_range == "last_year":
            start = now - timedelta(days=365)
        else:
            return "", params  # "all"

        params["start_date"] = start.date()
        return f"WHERE {date_col} >= :start_date", params

    @staticmethod
    async def calculate_kpis(
        db: AsyncSession,
        dataset_id: UUID,
        date_range: str = "last_30d",
    ) -> dict:
        """Calculate key performance indicators."""
        # Get dataset
        result = await db.execute(select(Dataset).where(Dataset.id == str(dataset_id)))
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise NotFoundException(f"Dataset {dataset_id} not found")

        schema = dataset.columns_schema or {}
        table_name = f"dataset_data_{dataset_id}"

        # Detect columns
        sales_col = AnalyticsService._detect_column(schema, "sales")
        profit_col = AnalyticsService._detect_column(schema, "profit")
        date_col = AnalyticsService._detect_column(schema, "date")
        quantity_col = AnalyticsService._detect_column(schema, "quantity")
        category_col = AnalyticsService._detect_column(schema, "category")

        if not all([sales_col, profit_col]):
            return {
                "error": "Dataset missing required columns (sales, profit)",
                "total_sales": 0,
                "total_profit": 0,
            }

        try:
            # Main query
            where_clause, params = AnalyticsService._get_date_filter(date_range, date_col) if date_col else ("", {})

            query = f"""
            SELECT 
                COUNT(*) as total_orders,
                SUM({sales_col}) as total_sales,
                SUM({profit_col}) as total_profit
            FROM {table_name}
            {where_clause}
            """

            result = await db.execute(text(query).bindparams(**params))
            row = result.mappings().first()

            if not row:
                return {"error": "No data found", "total_sales": 0}

            total_sales = float(row["total_sales"] or 0)
            total_profit = float(row["total_profit"] or 0)
            total_orders = int(row["total_orders"] or 0)

            # Calculate derived metrics
            profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
            avg_order_value = total_sales / total_orders if total_orders > 0 else 0

            # Top category
            top_category = "N/A"
            if category_col:
                cat_query = f"""
                SELECT {category_col}, SUM({sales_col}) as cat_sales
                FROM {table_name}
                {where_clause}
                GROUP BY {category_col}
                ORDER BY cat_sales DESC
                LIMIT 1
                """
                cat_result = await db.execute(text(cat_query).bindparams(**params))
                cat_row = cat_result.mappings().first()
                if cat_row:
                    top_category = str(cat_row[category_col])

            # Calculate growth vs previous period
            growth_pct = 0.0
            if date_col and date_range != "all":
                prev_range_map = {
                    "last_7d": 14,
                    "last_30d": 60,
                    "last_90d": 180,
                    "last_year": 730,
                }
                prev_days = prev_range_map.get(date_range, 30)
                prev_start = datetime.utcnow() - timedelta(days=prev_days)
                prev_params = {"prev_start": prev_start.date(), "start_date": params.get("start_date", datetime.utcnow().date())}

                prev_query = f"""
                SELECT SUM({sales_col}) as prev_sales
                FROM {table_name}
                WHERE {date_col} >= :prev_start AND {date_col} < :start_date
                """

                prev_result = await db.execute(text(prev_query).bindparams(**prev_params))
                prev_row = prev_result.mappings().first()
                prev_sales = float(prev_row["prev_sales"] or 1)
                growth_pct = ((total_sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0

            return {
                "total_sales": round(total_sales, 2),
                "total_profit": round(total_profit, 2),
                "profit_margin": round(profit_margin, 2),
                "total_orders": total_orders,
                "avg_order_value": round(avg_order_value, 2),
                "top_category": top_category,
                "growth_pct": round(growth_pct, 2),
                "period": date_range,
            }

        except Exception as e:
            logger.error(f"KPI calculation error: {str(e)}")
            return {"error": str(e), "total_sales": 0}

    @staticmethod
    async def get_sales_trend(
        db: AsyncSession,
        dataset_id: UUID,
        granularity: str = "daily",
        date_range: str = "last_30d",
    ) -> list:
        """Get sales trend over time."""
        result = await db.execute(select(Dataset).where(Dataset.id == str(dataset_id)))
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise NotFoundException(f"Dataset {dataset_id} not found")

        schema = dataset.columns_schema or {}
        table_name = f"dataset_data_{dataset_id}"

        sales_col = AnalyticsService._detect_column(schema, "sales")
        profit_col = AnalyticsService._detect_column(schema, "profit")
        date_col = AnalyticsService._detect_column(schema, "date")

        if not all([sales_col, date_col]):
            return []

        try:
            # Truncate date based on granularity
            date_trunc = {
                "daily": "date",
                "weekly": "week",
                "monthly": "month",
            }.get(granularity, "date")

            where_clause, params = AnalyticsService._get_date_filter(date_range, date_col) if date_col else ("", {})

            query = f"""
            SELECT 
                DATE_TRUNC('{date_trunc}', {date_col})::date as period,
                SUM({sales_col}) as sales,
                SUM({profit_col}) as profit,
                COUNT(*) as orders
            FROM {table_name}
            {where_clause}
            GROUP BY DATE_TRUNC('{date_trunc}', {date_col})
            ORDER BY period ASC
            """

            result = await db.execute(text(query).bindparams(**params))
            rows = result.mappings().all()

            return [
                {
                    "date": str(row["period"]),
                    "sales": float(row["sales"] or 0),
                    "profit": float(row["profit"] or 0),
                    "orders": int(row["orders"] or 0),
                }
                for row in rows
            ]

        except Exception as e:
            logger.error(f"Sales trend error: {str(e)}")
            return []

    @staticmethod
    async def get_category_breakdown(
        db: AsyncSession,
        dataset_id: UUID,
        metric: str = "sales",
    ) -> list:
        """Get breakdown by category."""
        result = await db.execute(select(Dataset).where(Dataset.id == str(dataset_id)))
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise NotFoundException(f"Dataset {dataset_id} not found")

        schema = dataset.columns_schema or {}
        table_name = f"dataset_data_{dataset_id}"

        metric_col = AnalyticsService._detect_column(schema, metric)
        category_col = AnalyticsService._detect_column(schema, "category")

        if not all([metric_col, category_col]):
            return []

        try:
            query = f"""
            SELECT 
                {category_col} as category,
                SUM({metric_col}) as value
            FROM {table_name}
            GROUP BY {category_col}
            ORDER BY value DESC
            """

            result = await db.execute(text(query))
            rows = result.mappings().all()

            total = sum(float(row["value"] or 0) for row in rows)

            return [
                {
                    "category": str(row["category"]),
                    "value": float(row["value"] or 0),
                    "pct": round((float(row["value"] or 0) / total * 100) if total > 0 else 0, 1),
                }
                for row in rows
            ]

        except Exception as e:
            logger.error(f"Category breakdown error: {str(e)}")
            return []

    @staticmethod
    async def get_regional_performance(
        db: AsyncSession,
        dataset_id: UUID,
        metric: str = "sales",
    ) -> list:
        """Get performance by region."""
        result = await db.execute(select(Dataset).where(Dataset.id == str(dataset_id)))
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise NotFoundException(f"Dataset {dataset_id} not found")

        schema = dataset.columns_schema or {}
        table_name = f"dataset_data_{dataset_id}"

        metric_col = AnalyticsService._detect_column(schema, metric)
        region_col = AnalyticsService._detect_column(schema, "region")

        if not all([metric_col, region_col]):
            return []

        try:
            query = f"""
            SELECT 
                {region_col} as region,
                SUM({metric_col}) as value,
                COUNT(*) as count
            FROM {table_name}
            GROUP BY {region_col}
            ORDER BY value DESC
            """

            result = await db.execute(text(query))
            rows = result.mappings().all()

            return [
                {
                    "region": str(row["region"]),
                    "value": float(row["value"] or 0),
                    "count": int(row["count"] or 0),
                }
                for row in rows
            ]

        except Exception as e:
            logger.error(f"Regional performance error: {str(e)}")
            return []

    @staticmethod
    async def get_top_products(
        db: AsyncSession,
        dataset_id: UUID,
        limit: int = 10,
        sort_by: str = "sales",
    ) -> list:
        """Get top products by metric."""
        result = await db.execute(select(Dataset).where(Dataset.id == str(dataset_id)))
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise NotFoundException(f"Dataset {dataset_id} not found")

        schema = dataset.columns_schema or {}
        table_name = f"dataset_data_{dataset_id}"

        product_col = AnalyticsService._detect_column(schema, "product")
        category_col = AnalyticsService._detect_column(schema, "category")
        sales_col = AnalyticsService._detect_column(schema, "sales")
        profit_col = AnalyticsService._detect_column(schema, "profit")
        quantity_col = AnalyticsService._detect_column(schema, "quantity")

        if not product_col or not sales_col:
            return []

        sort_metric = {
            "sales": sales_col,
            "profit": profit_col or sales_col,
            "quantity": quantity_col or sales_col,
        }.get(sort_by, sales_col)

        try:
            query = f"""
            SELECT 
                {product_col} as product,
                {category_col if category_col else "'N/A'" } as category,
                SUM({sales_col}) as sales,
                SUM({profit_col}) as profit,
                SUM({quantity_col}) as quantity,
                ROUND(SUM({profit_col})::NUMERIC / NULLIF(SUM({sales_col}), 0) * 100, 2) as margin
            FROM {table_name}
            GROUP BY {product_col}{f', {category_col}' if category_col else ''}
            ORDER BY {sort_metric} DESC
            LIMIT {limit}
            """

            result = await db.execute(text(query))
            rows = result.mappings().all()

            return [
                {
                    "product": str(row["product"]),
                    "category": str(row["category"]),
                    "sales": float(row["sales"] or 0),
                    "profit": float(row["profit"] or 0),
                    "quantity": float(row["quantity"] or 0),
                    "margin": float(row["margin"] or 0),
                }
                for row in rows
            ]

        except Exception as e:
            logger.error(f"Top products error: {str(e)}")
            return []

    @staticmethod
    async def get_discount_analysis(
        db: AsyncSession,
        dataset_id: UUID,
    ) -> dict:
        """Analyze discount vs profit correlation."""
        result = await db.execute(select(Dataset).where(Dataset.id == str(dataset_id)))
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise NotFoundException(f"Dataset {dataset_id} not found")

        schema = dataset.columns_schema or {}
        table_name = f"dataset_data_{dataset_id}"

        discount_col = AnalyticsService._detect_column(schema, "discount")
        profit_col = AnalyticsService._detect_column(schema, "profit")
        sales_col = AnalyticsService._detect_column(schema, "sales")

        if not all([discount_col, profit_col, sales_col]):
            return {"correlation": 0, "data": [], "insight": "Missing required columns"}

        try:
            query = f"""
            SELECT 
                {discount_col} as discount,
                {profit_col} as profit,
                {sales_col} as sales
            FROM {table_name}
            WHERE {discount_col} IS NOT NULL AND {profit_col} IS NOT NULL
            ORDER BY {discount_col} ASC
            """

            result = await db.execute(text(query))
            rows = result.mappings().all()

            data_points = [
                {
                    "discount": float(row["discount"] or 0),
                    "profit": float(row["profit"] or 0),
                    "sales": float(row["sales"] or 0),
                }
                for row in rows
            ]

            if len(data_points) < 2:
                return {"correlation": 0, "data": data_points, "insight": "Insufficient data"}

            # Calculate Pearson correlation
            discounts = [p["discount"] for p in data_points]
            profits = [p["profit"] for p in data_points]

            mean_d = statistics.mean(discounts)
            mean_p = statistics.mean(profits)

            covariance = sum((d - mean_d) * (p - mean_p) for d, p in zip(discounts, profits)) / len(data_points)
            std_d = statistics.stdev(discounts) if len(set(discounts)) > 1 else 1
            std_p = statistics.stdev(profits) if len(set(profits)) > 1 else 1

            correlation = covariance / (std_d * std_p) if (std_d > 0 and std_p > 0) else 0

            insight = f"{'Strong negative' if correlation < -0.5 else 'Weak negative' if correlation < 0 else 'Weak positive' if correlation < 0.5 else 'Strong positive'} correlation ({correlation:.2f}) between discount and profit."

            return {
                "correlation": round(correlation, 3),
                "data": data_points[:100],  # Limit for performance
                "insight": insight,
            }

        except Exception as e:
            logger.error(f"Discount analysis error: {str(e)}")
            return {"correlation": 0, "data": [], "insight": f"Error: {str(e)}"}

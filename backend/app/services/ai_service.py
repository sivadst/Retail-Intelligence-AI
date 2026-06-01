"""AI-powered analytics assistant with NL to SQL conversion."""
import json
import logging
import re
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from openai import AsyncOpenAI

from app.config import settings
from app.models import Dataset, ChatMessage
from app.core import NotFoundException, ValidationException

logger = logging.getLogger(__name__)

# Forbidden SQL keywords - reject any query containing these
FORBIDDEN_KEYWORDS = r'\b(INSERT|UPDATE|DELETE|ALTER|DROP|CREATE|TRUNCATE|GRANT|REVOKE|EXECUTE|SCRIPT|EXEC)\b'


class AIService:
    """AI-powered analytics service."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    @staticmethod
    async def build_schema_context(
        db: AsyncSession,
        dataset_id: UUID,
    ) -> str:
        """Build schema context string for LLM."""
        result = await db.execute(select(Dataset).where(Dataset.id == str(dataset_id)))
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise NotFoundException(f"Dataset {dataset_id} not found")

        schema = dataset.columns_schema or {}
        table_name = f"dataset_data_{dataset_id}"

        # Build schema description
        lines = [
            f"Table: {table_name}",
            "Columns:",
        ]

        if schema.get("columns"):
            for col_name, col_type in schema["columns"].items():
                lines.append(f"- {col_name} ({col_type})")

        lines.extend([
            "",
            "Rules:",
            "- Always SELECT only necessary columns",
            "- Use appropriate WHERE clauses for filtering",
            "- Include GROUP BY when using aggregates",
            "- Use LIMIT to cap result size",
            "- Never modify data (no INSERT/UPDATE/DELETE)",
        ])

        return "\n".join(lines)

    async def generate_sql(
        self,
        question: str,
        dataset_id: UUID,
        db: AsyncSession,
    ) -> dict:
        """Convert natural language to SQL using GPT-4o."""
        schema_context = await self.build_schema_context(db, dataset_id)
        table_name = f"dataset_data_{dataset_id}"

        system_prompt = f"""You are an expert retail data analyst. Convert the user's question into a PostgreSQL SELECT query.

SCHEMA:
{schema_context}

RULES:
- ONLY SELECT statements. Never INSERT/UPDATE/DELETE/ALTER/DROP.
- Use exact column and table names from schema.
- Handle dates with PostgreSQL date functions.
- Use GROUP BY with aggregates.
- Limit results to 1000 rows.
- Return valid PostgreSQL syntax.

Respond in JSON:
{{
  "sql": "SELECT ...",
  "explanation": "what this query does",
  "chart_type": "bar|line|pie|table|scatter|none",
  "title": "chart title"
}}"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            result = json.loads(response.choices[0].message.content)

            # Validate SQL
            if not self._validate_sql(result.get("sql", "")):
                raise ValidationException("Generated SQL contains forbidden operations")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            raise ValidationException("Invalid response from AI")

    @staticmethod
    def _validate_sql(sql: str) -> bool:
        """Check SQL for forbidden operations."""
        if re.search(FORBIDDEN_KEYWORDS, sql, re.IGNORECASE):
            return False
        return True

    @staticmethod
    async def execute_safe_sql(
        sql: str,
        dataset_id: UUID,
        db: AsyncSession,
    ) -> list:
        """Execute parameterized SQL safely."""
        if not AIService._validate_sql(sql):
            raise ValidationException("SQL contains forbidden operations")

        try:
            # Limit to prevent abuse
            if "LIMIT" not in sql.upper():
                sql = f"{sql} LIMIT 1000"

            result = await db.execute(text(sql))
            rows = result.mappings().all()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"SQL execution error: {str(e)}")
            raise ValidationException(f"Query execution failed: {str(e)}")

    async def generate_insight(
        self,
        question: str,
        sql: str,
        results: list,
        schema_context: str,
    ) -> str:
        """Generate human-readable insight from query results."""
        # Limit result size for prompt
        result_sample = json.dumps(results[:50], default=str)

        insight_prompt = f"""The user asked: {question}

The SQL query executed was:
{sql}

The query results are:
{result_sample}

Provide a clear, actionable insight based on this data.
- Include specific numbers and percentages
- Highlight trends or anomalies
- Keep it concise (2-3 sentences)
- Focus on what's interesting or actionable"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "user", "content": insight_prompt},
                ],
                temperature=0.3,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Insight generation error: {str(e)}")
            return "Unable to generate insight at this time"

    async def get_suggested_questions(
        self,
        dataset_id: UUID,
        db: AsyncSession,
    ) -> list:
        """Generate suggested questions based on dataset schema."""
        result = await db.execute(select(Dataset).where(Dataset.id == str(dataset_id)))
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise NotFoundException(f"Dataset {dataset_id} not found")

        schema = dataset.columns_schema or {}
        columns = list(schema.get("columns", {}).keys())

        if not columns:
            return []

        # Build context about available data
        columns_str = ", ".join(columns[:10])

        prompt = f"""Based on a retail dataset with columns: {columns_str}

Generate 5 specific, actionable questions a retail analyst would ask.
Format as JSON array of strings:
["question 1", "question 2", ...]

Make questions specific to retail (sales, profit, categories, regions, discounts, trends)"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )

            # Parse response
            content = response.choices[0].message.content
            if content.startswith("["):
                questions = json.loads(content)
            else:
                # If wrapped in JSON object, extract array
                data = json.loads(content)
                questions = data if isinstance(data, list) else list(data.values())[0]

            return questions[:5]

        except Exception as e:
            logger.error(f"Suggested questions error: {str(e)}")
            # Return default questions
            return [
                "What were the top 5 categories by profit?",
                "How did sales trend over time?",
                "Which regions performed best?",
                "What's the relationship between discount and profit?",
                "What are our top products by revenue?",
            ]

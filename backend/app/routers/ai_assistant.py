"""AI assistant routes."""
import logging
import uuid
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user, require_permission
from app.models import User, ChatMessage, Dataset
from app.schemas import ChatMessageResponse
from app.core import Permission, NotFoundException
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

ai_service = AIService()


class ChatRequest(BaseModel):
    """Chat request."""
    message: str
    dataset_id: str
    conversation_id: str = None


class ChatResponse(BaseModel):
    """Chat response."""
    success: bool
    data: dict


async def verify_dataset_access(dataset_id: str, current_user: User, db: AsyncSession):
    """Verify dataset access."""
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.organization_id == current_user.organization_id,
        )
    )
    if not result.scalar_one_or_none():
        raise NotFoundException("Dataset not found or access denied")


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(require_permission(Permission.USE_AI_ASSISTANT)),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """Send message to AI assistant."""
    # Verify dataset access
    await verify_dataset_access(request.dataset_id, current_user, db)

    # Generate conversation ID if not provided
    conversation_id = request.conversation_id or str(uuid.uuid4())

    # Store user message
    user_msg = ChatMessage(
        user_id=current_user.id,
        conversation_id=conversation_id,
        message_type="user",
        content=request.message,
    )
    db.add(user_msg)
    await db.commit()

    try:
        # Generate SQL from question
        sql_response = await ai_service.generate_sql(
            request.message,
            request.dataset_id,
            db,
        )

        sql = sql_response.get("sql")
        chart_type = sql_response.get("chart_type", "table")

        # Execute SQL
        results = await ai_service.execute_safe_sql(sql, request.dataset_id, db)

        # Generate insight
        schema_context = await ai_service.build_schema_context(db, request.dataset_id)
        insight = await ai_service.generate_insight(
            request.message,
            sql,
            results,
            schema_context,
        )

        # Store assistant message
        assistant_msg = ChatMessage(
            user_id=current_user.id,
            conversation_id=conversation_id,
            message_type="assistant",
            content=insight,
            sql_query=sql,
            chart_type=chart_type,
        )
        db.add(assistant_msg)
        await db.commit()

        return ChatResponse(
            success=True,
            data={
                "message": insight,
                "sql_query": sql,
                "results": results[:100],  # Limit for frontend
                "chart_type": chart_type,
                "conversation_id": conversation_id,
            },
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        # Store error message
        error_msg = ChatMessage(
            user_id=current_user.id,
            conversation_id=conversation_id,
            message_type="assistant",
            content=f"Error processing your query: {str(e)}",
        )
        db.add(error_msg)
        await db.commit()

        return ChatResponse(
            success=False,
            data={"message": f"Error: {str(e)}", "conversation_id": conversation_id},
        )


@router.get("/suggested-questions")
async def get_suggested_questions(
    dataset_id: str = Query(...),
    current_user: User = Depends(require_permission(Permission.USE_AI_ASSISTANT)),
    db: AsyncSession = Depends(get_db),
):
    """Get suggested questions for dataset."""
    await verify_dataset_access(dataset_id, current_user, db)

    questions = await ai_service.get_suggested_questions(dataset_id, db)
    return {"success": True, "data": {"questions": questions}}


@router.get("/conversations")
async def list_conversations(
    current_user: User = Depends(require_permission(Permission.USE_AI_ASSISTANT)),
    db: AsyncSession = Depends(get_db),
):
    """List user's conversations."""
    result = await db.execute(
        select(ChatMessage.conversation_id)
        .where(ChatMessage.user_id == current_user.id)
        .distinct()
        .order_by(ChatMessage.conversation_id)
    )
    conversations = result.scalars().all()
    return {"success": True, "data": {"conversations": list(conversations)}}


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(require_permission(Permission.USE_AI_ASSISTANT)),
    db: AsyncSession = Depends(get_db),
):
    """Get conversation history."""
    result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.conversation_id == conversation_id,
            ChatMessage.user_id == current_user.id,
        )
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()

    return {
        "success": True,
        "data": [
            {
                "id": m.id,
                "role": m.message_type,
                "content": m.content,
                "sql_query": m.sql_query,
                "chart_type": m.chart_type,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
    }

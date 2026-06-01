"""AI assistant routes."""
import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user, require_permission
from app.models import User, ChatMessage
from app.schemas import ChatMessageCreate, ChatMessageResponse
from app.core import Permission

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: ChatMessageCreate,
    current_user: User = Depends(require_permission(Permission.USE_AI_ASSISTANT)),
    db: AsyncSession = Depends(get_db),
) -> ChatMessageResponse:
    """Send message to AI assistant."""
    # Store user message
    user_message = ChatMessage(
        user_id=current_user.id,
        conversation_id=message_data.conversation_id,
        message_type="user",
        content=message_data.content,
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)

    logger.info(f"Chat message from {current_user.email}: {message_data.conversation_id}")

    # TODO: Process with LLM and generate response
    # For now, return the user message
    return ChatMessageResponse.from_orm(user_message)


@router.get("/conversations/{conversation_id}", response_model=list[ChatMessageResponse])
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(require_permission(Permission.USE_AI_ASSISTANT)),
    db: AsyncSession = Depends(get_db),
) -> list[ChatMessageResponse]:
    """Get chat conversation."""
    result = await db.execute(
        select(ChatMessage).where(
            ChatMessage.conversation_id == conversation_id,
            ChatMessage.user_id == current_user.id,
        )
    )
    messages = result.scalars().all()
    return [ChatMessageResponse.from_orm(m) for m in messages]

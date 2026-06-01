from fastapi import APIRouter

from app.schemas.product import ChatRequest, ChatResponse
from app.services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    return ChatResponse(**chat_service.answer_question(payload.slug, payload.question))

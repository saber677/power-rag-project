from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.llm import chat, chat_stream
from app.scheduler import run_increment, run_rebuild

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


@router.post("/chat")
async def api_chat(req: ChatRequest) -> ChatResponse:
    """同步问答接口"""
    result = chat(req.question)
    return ChatResponse(**result)


@router.post("/chat/stream")
async def api_chat_stream(req: ChatRequest):
    """流式问答接口"""
    return StreamingResponse(
        chat_stream(req.question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/index/rebuild")
async def api_rebuild():
    run_rebuild()
    return {"status": "ok", "message": "Full rebuild completed"}


@router.post("/index/increment")
async def api_increment():
    run_increment()
    return {"status": "ok", "message": "Increment scan completed"}


@router.get("/health")
async def health():
    return {"status": "ok"}

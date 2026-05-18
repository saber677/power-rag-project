from fastapi import APIRouter
from pydantic import BaseModel

from app.llm import chat
from app.scheduler import run_increment, run_rebuild

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


@router.post("/chat")
async def api_chat(req: ChatRequest) -> ChatResponse:
    result = chat(req.question)
    return ChatResponse(**result)


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

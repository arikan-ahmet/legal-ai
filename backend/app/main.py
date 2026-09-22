from fastapi import FastAPI
from pydantic import BaseModel

from app.llm import LLMService


app = FastAPI(
    title="Legal AI API",
    description="Backend API for the Legal AI platform.",
    version="0.1.0",
)


llm_service = LLMService()


class ChatRequest(BaseModel):
    message: str


@app.get("/")
async def root():
    return {"message": "Legal AI API is running!"}


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "legal-ai-backend",
        "version": "0.1.0",
    }


@app.post("/chat")
async def chat(request: ChatRequest):
    answer = llm_service.chat(request.message)

    return {
        "answer": answer
    }
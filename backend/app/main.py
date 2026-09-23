from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.llm import LLMService


app = FastAPI(
    title="Legal AI API",
    description="Backend API for the Legal AI platform.",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
conversations = {}


llm_service = LLMService()


class ChatRequest(BaseModel):
    conversation_id: str
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

async def generate_response(history, llm_service):
    answer = ""

    async for chunk in llm_service.chat_stream(history):
        answer += chunk
        yield chunk

    history.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

@app.post("/chat")
async def chat(
    request: ChatRequest,
    llm_service: LLMService = Depends(LLMService),
):
    if request.conversation_id not in conversations:
        conversations[request.conversation_id] = []

    history = conversations[request.conversation_id]
    history.append(
        {
            "role": "user",
            "content": request.message,
        }
    )

    try:
        return StreamingResponse(
            generate_response(history, llm_service),
            media_type="text/plain",
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        )
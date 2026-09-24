from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.llm import LLMService
from pathlib import Path
from uuid import uuid4
from app.rag.indexer import load_index
from app.rag.retriever import Retriever
from app.rag.context import build_context

app = FastAPI(
    title="Legal AI API",
    description="Backend API for the Legal AI platform.",
    version="0.1.0",
)
index, chunks = load_index(Path("data/vector_store"))
retriever = Retriever(index, chunks)
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
    
class RetrieveRequest(BaseModel):
    question: str
    top_k: int = 5

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

async def generate_response(history, context, llm_service):
    messages = [
        {
            "role": "system",
            "content": (
                "Sen Türk hukuk alanında çalışan bir yapay zeka asistanısın. "
                "Cevaplarını yalnızca aşağıdaki kaynaklarda verilen bilgilere "
                "dayandır. Kaynaklarda cevap bulunmuyorsa bunu açıkça belirt.\n\n"
                f"KAYNAKLAR:\n{context}"
            ),
        },
        *history,
    ]

    answer = ""

    async for chunk in llm_service.chat_stream(messages):
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
    results = retriever.retrieve(
        request.message,
        top_k=5,
    )

    context = build_context(results)
    try:
        return StreamingResponse(
            generate_response(history, context, llm_service),
            media_type="text/plain",
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        )

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    documents_dir = Path("data/documents")
    documents_dir.mkdir(parents=True, exist_ok=True)

    document_id = uuid4()
    file_path = documents_dir / f"{document_id}.pdf"

    with file_path.open("wb") as buffer:
        buffer.write(await file.read())

    return {
        "document_id": str(document_id),
        "filename": file.filename,
    }

@app.post("/retrieve")
async def retrieve_documents(request: RetrieveRequest):
    results = retriever.retrieve(
        request.question,
        top_k=request.top_k,
    )

    return {"results": results}
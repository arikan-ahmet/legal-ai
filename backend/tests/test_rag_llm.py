import asyncio
from pathlib import Path

from app.llm import LLMService
from app.rag.context import build_context
from app.rag.indexer import load_index
from app.rag.retriever import Retriever


async def main():
    index, chunks = load_index(Path("data/vector_store"))
    retriever = Retriever(index, chunks)

    question = "Sözleşme nasıl kurulur?"

    results = retriever.retrieve(question, top_k=3)
    context = build_context(results)
    print("CONTEXT LENGTH:", len(context))
    print("CONTEXT:")
    print(context)

    messages = [
        {
            "role": "system",
            "content": (
                "Sen Türk hukuk alanında çalışan bir yapay zeka asistanısın. "
                "Cevabını yalnızca verilen kaynaklara dayanarak ver. "
                "Kaynaklarda cevap yoksa bunu açıkça belirt.\n\n"
                f"KAYNAKLAR:\n{context}"
            ),
        },
        {
            "role": "user",
            "content": question,
        },
    ]

    llm_service = LLMService()

    print("Sending request to Qwen...")

    print("Calling LLMService.chat()...")

    try:
        answer = await asyncio.wait_for(
            llm_service.chat(messages),
            timeout=30.0,
        )

        print("\nANSWER:")
        print(answer)

    except asyncio.TimeoutError:
        print("\nTIMEOUT: LLM did not respond within 30 seconds.")


asyncio.run(main())
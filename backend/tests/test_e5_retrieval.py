from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.rag.chunker import chunk_legal_pages
from app.rag.parser import extract_text_from_pdf


PDF_PATH = Path(
    "data/documents/1b02f155-60ef-4bc6-a163-14b824a1c8e9.pdf"
)

MODEL_NAME = "intfloat/multilingual-e5-small"


pages = extract_text_from_pdf(PDF_PATH)
chunks = chunk_legal_pages(pages)

model = SentenceTransformer(MODEL_NAME, device="cuda")

passages = [f"passage: {chunk['text']}" for chunk in chunks]

embeddings = model.encode(
    passages,
    normalize_embeddings=True,
    show_progress_bar=True,
)

embeddings = np.asarray(embeddings, dtype="float32")

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)


questions = [
    ("Sözleşme nasıl kurulur?", 1),
    ("Sözleşme ne zaman kurulmuş sayılır?", 1),
    ("Sözleşmenin şekli nasıl olmalıdır?", 12),
    ("Haksız fiilden doğan borçlarda zamanaşımı ne kadardır?", 72),
    ("Borçlu ne zaman temerrüde düşer?", 117),
]


top1_correct = 0
top5_correct = 0

for question, expected_article in questions:
    query_embedding = model.encode(
        [f"query: {question}"],
        normalize_embeddings=True,
    )

    query_embedding = np.asarray(query_embedding, dtype="float32")

    scores, indices = index.search(query_embedding, 5)

    retrieved_articles = [
        chunks[idx]["article_number"]
        for idx in indices[0]
    ]
    for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
        chunk = chunks[idx]

        print(
            f"{rank}. score={score:.4f} "
            f"article={chunk['article_number']} "
            f"page={chunk['page_number']}"
        )
        print(chunk["text"][:300].replace("\n", " "))

    if retrieved_articles[0] == expected_article:
        top1_correct += 1

    if expected_article in retrieved_articles:
        top5_correct += 1

    print(f"\nQUESTION: {question}")
    print(f"Expected article: {expected_article}")
    print(f"Retrieved articles: {retrieved_articles}")

print("\n--- RESULTS ---")
print(f"Top-1 accuracy: {top1_correct / len(questions):.2%}")
print(f"Top-5 accuracy: {top5_correct / len(questions):.2%}")
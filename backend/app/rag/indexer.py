from pathlib import Path
import json

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.rag.chunker import chunk_legal_pages
from app.rag.parser import extract_text_from_pdf


MODEL_NAME = "intfloat/multilingual-e5-small"


def build_index(pdf_path: Path):
    pages = extract_text_from_pdf(pdf_path)
    chunks = chunk_legal_pages(pages)

    texts = [f"passage: {chunk['text']}" for chunk in chunks]

    model = SentenceTransformer(
        MODEL_NAME,
        device="cuda",
    )

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    embeddings = np.asarray(embeddings, dtype="float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    return index, chunks


def save_index(index, chunks, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    faiss.write_index(
        index,
        str(output_dir / "index.faiss"),
    )

    with (output_dir / "chunks.json").open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2,
        )

def load_index(input_dir: Path):
    index = faiss.read_index(
        str(input_dir / "index.faiss")
    )

    with (input_dir / "chunks.json").open(
        "r",
        encoding="utf-8",
    ) as file:
        chunks = json.load(file)

    return index, chunks


if __name__ == "__main__":
    pdf_path = Path(
        "data/documents/1b02f155-60ef-4bc6-a163-14b824a1c8e9.pdf"
    )
    output_dir = Path("data/vector_store")

    index, chunks = build_index(pdf_path)
    save_index(index, chunks, output_dir)

    print(f"Saved {len(chunks)} chunks.")
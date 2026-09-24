import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "intfloat/multilingual-e5-small"


class Retriever:
    def __init__(self, index, chunks):
        self.index = index
        self.chunks = chunks

        self.model = SentenceTransformer(
            MODEL_NAME,
            device="cpu",
        )

    def retrieve(self, question: str, top_k: int = 5) -> list[dict]:
        query_embedding = self.model.encode(
            [f"query: {question}"],
            normalize_embeddings=True,
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32",
        )

        scores, indices = self.index.search(
            query_embedding,
            top_k,
        )

        results = []

        for score, index in zip(scores[0], indices[0]):

            results.append(
                {
                    "score": float(score),
                    "page_number": self.chunks[index]["page_number"],
                    "article_number": self.chunks[index]["article_number"],
                    "text": self.chunks[index]["text"],
                }
            )

        return results
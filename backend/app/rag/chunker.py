import re

def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start += chunk_size - overlap

    return chunks

def chunk_pages(
    pages: list[dict],
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[dict]:
    chunks = []

    for page in pages:
        page_chunks = chunk_text(
            page["text"],
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk in page_chunks:
            chunks.append(
                {
                    "page_number": page["page_number"],
                    "text": chunk,
                }
            )

    return chunks

def chunk_legal_pages(
    pages: list[dict],
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[dict]:
    chunks = []

    current_article = None

    for page in pages:
        text = page["text"]
        page_number = page["page_number"]

        parts = re.split(r"(?=MADDE\s+\d+\s*-)", text)

        for part in parts:
            part = part.strip()

            if not part:
                continue

            article_match = re.match(r"MADDE\s+(\d+)\s*-", part)

            if article_match:
                current_article = int(article_match.group(1))

            if len(part) <= chunk_size:
                chunks.append(
                    {
                        "page_number": page_number,
                        "article_number": current_article,
                        "text": part,
                    }
                )
            else:
                sub_chunks = chunk_text(
                    part,
                    chunk_size=chunk_size,
                    overlap=overlap,
                )

                for sub_chunk in sub_chunks:
                    chunks.append(
                        {
                            "page_number": page_number,
                            "article_number": current_article,
                            "text": sub_chunk,
                        }
                    )

    return chunks
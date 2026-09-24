def build_context(results: list[dict]) -> str:
    context_parts = []

    for i, result in enumerate(results, start=1):
        source = (
            f"KAYNAK {i}\n"
            f"Madde: {result['article_number']}\n"
            f"Sayfa: {result['page_number']}\n"
            f"Metin:\n{result['text']}"
        )

        context_parts.append(source)

    return "\n\n".join(context_parts)
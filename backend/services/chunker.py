def clean_text(text):

    lines = text.splitlines()

    cleaned = []

    for line in lines:

        line = line.strip()

        if line:
            cleaned.append(line)

    return " ".join(cleaned)


def create_chunks(
    pages,
    chunk_size=1000,
    overlap=150
):

    chunks = []

    for page in pages:

        text = clean_text(
            page["text"]
        )

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end]

            chunks.append({
                "text": chunk_text,
                "page": page["page"]
            })

            start += (
                chunk_size - overlap
            )

    return chunks
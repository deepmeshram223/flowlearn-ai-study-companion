from sentence_transformers import SentenceTransformer

# Load the model only once
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text):
    """
    Generate an embedding for a single piece of text.
    """
    embedding = model.encode(
        text,
        convert_to_numpy=True,
        show_progress_bar=False
    )

    return embedding.tolist()


def generate_embeddings(texts, batch_size=32):
    """
    Generate embeddings for multiple texts in batches.

    This is much faster than calling generate_embedding()
    separately for every chunk.
    """

    if not texts:
        return []

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        convert_to_numpy=True,
        show_progress_bar=False
    )

    return embeddings.tolist()
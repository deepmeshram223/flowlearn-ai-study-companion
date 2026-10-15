from backend.services.embeddings import generate_embedding
from backend.services.vector_store import save_document, save_chunk


document_id = save_document(
    "test.pdf",
    "pdf"
)

text = "An operating system manages computer hardware and software resources."

embedding = generate_embedding(text)

chunk_id = save_chunk(
    document_id=document_id,
    chunk_text=text,
    page_number=1,
    embedding=embedding
)

print("Document ID:", document_id)
print("Embedding dimensions:", len(embedding))
print("Chunk ID:", chunk_id)
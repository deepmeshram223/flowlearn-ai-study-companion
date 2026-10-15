from backend.services.embeddings import generate_embedding
from backend.services.vector_store import search_similar_chunks


question = "What does an operating system do?"

query_embedding = generate_embedding(question)

results = search_similar_chunks(
    query_embedding,
    limit=5
)

print("\nSearch Results:\n")

for result in results:
    print("Distance:", result["distance"])
    print("Page:", result["page_number"])
    print("Text:", result["chunk_text"])
    print("-" * 60)
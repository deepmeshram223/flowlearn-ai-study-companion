from backend.services.embeddings import generate_embedding


text = "What is an operating system?"


embedding = generate_embedding(
    text
)


print("Embedding generated!")
print("Number of values:", len(embedding))
print("First 10 values:", embedding[:10])
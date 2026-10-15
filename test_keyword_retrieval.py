from backend.services.embeddings import generate_embedding
from backend.services.vector_store import (
    search_similar_chunks_for_document
)


questions = [
    "NDB navigation beacon",
    "marshalling signals and their types",
    "NDB navigation beacon and marshalling signals"
]

document_id = 54


for question in questions:

    print("\n")
    print("=" * 100)
    print("QUESTION:", question)
    print("=" * 100)

    embedding = generate_embedding(question)

    results = search_similar_chunks_for_document(
        query_embedding=embedding,
        document_id=document_id,
        limit=10,
        search_terms=question.lower().replace(",", "").split()
    )

    for index, result in enumerate(results, start=1):

        print("\n" + "-" * 100)

        print(
            f"RESULT {index} | "
            f"PAGE: {result['page_number']} | "
            f"DISTANCE: {result['distance']} | "
            f"KEYWORD SCORE: {result.get('keyword_score', 0)}"
        )

        print("-" * 100)

        print(result["chunk_text"][:1000])
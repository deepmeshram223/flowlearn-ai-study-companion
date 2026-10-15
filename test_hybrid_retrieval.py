from backend.services.rag import retrieve_context


document_id = 54

questions = [
    "NDB navigation beacon",
    "marshalling signals and their types",
    "Tell me about NDB navigation beacon and marshalling signals"
]


for question in questions:

    print("\n")
    print("=" * 100)
    print("QUESTION:", question)
    print("=" * 100)

    results = retrieve_context(
        question=question,
        document_id=document_id,
        limit=10
    )

    for index, result in enumerate(results, start=1):

        print("\n" + "-" * 100)

        print(
            f"RESULT {index} | "
            f"Page: {result['page_number']} | "
            f"Distance: {result['distance']}"
        )

        print("-" * 100)

        print(result["chunk_text"][:1000])
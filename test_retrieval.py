from backend.services.rag import retrieve_context


def test_query(query):
    print("\n" + "=" * 80)
    print("QUERY:", query)
    print("=" * 80)

    results = retrieve_context(
        query,
        document_id=54,
        limit=10
    )

    for i, result in enumerate(results, 1):

        print(f"\nRESULT {i}")
        print("-" * 80)

        print(
            "PAGE:",
            result["page_number"]
        )

        print(
            "DISTANCE:",
            result["distance"]
        )

        print("\nTEXT:")

        print(
            result["chunk_text"][:1000]
        )


test_query(
    "marshalling signals and their types"
)

test_query(
    "NDB navigation beacon"
)

test_query(
    "Tell me about marshalling signals and their types and also give information about NDB"
)
from backend.services.rag import retrieve_context, build_context


question = "What responsibilities are mentioned in the Roshverse Games internship?"


results = retrieve_context(
    question,
    limit=5
)


print("\nRetrieved Chunks:\n")


for result in results:
    print("Document ID:", result["document_id"])
    print("Page:", result["page_number"])
    print("Distance:", result["distance"])
    print("Text:", result["chunk_text"])
    print("-" * 80)


context = build_context(results)


print("\n\nCombined Context:\n")
print(context)
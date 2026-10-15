from backend.services.rag import answer_question


question = "What is the salary offered by Roshverse Games?"


result = answer_question(
    question,
    limit=5
)


print("\n==============================")
print("ANSWER")
print("==============================\n")

print(result["answer"])


print("\n==============================")
print("SOURCES")
print("==============================\n")


for source in result["sources"]:
    print(
        f"Document ID: {source['document_id']} | "
        f"Page: {source['page_number']} | "
        f"Distance: {source['distance']}"
    )

    print(source["chunk_text"])
    print("-" * 70)
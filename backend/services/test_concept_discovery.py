from backend.services.concept_discovery import (
    discover_topics
)


DOCUMENT_ID = 54


clusters = discover_topics(
    document_id=DOCUMENT_ID,
    number_of_topics=30
)


print("\n================================")
print("CONCEPT DISCOVERY RESULTS")
print("================================")

print(
    f"Total clusters: {len(clusters)}"
)


for cluster in clusters:

    print(
        f"\n--- Cluster "
        f"{cluster['cluster_id']} ---"
    )

    print(
        f"Chunks: "
        f"{cluster['chunk_count']}"
    )

    print(
        "Representative chunks:"
    )

    for chunk in cluster[
        "representative_chunks"
    ]:

        print(
            f"Page {chunk['page']}: "
            f"{chunk['text'][:250]}..."
        )


print(
    "\n================================"
)
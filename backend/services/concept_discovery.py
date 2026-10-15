import numpy as np

from sqlalchemy import text

from backend.database.connection import engine


def get_document_embeddings(document_id):
    """
    Load all chunk embeddings for a document.
    """

    query = text("""
        SELECT
            id,
            chunk_text,
            page_number,
            embedding
        FROM document_chunks
        WHERE document_id = :document_id
        ORDER BY id;
    """)

    with engine.connect() as connection:

        rows = connection.execute(
            query,
            {
                "document_id": document_id
            }
        ).mappings().all()

    return rows


def parse_embedding(embedding):
    """
    Convert PostgreSQL vector value into a Python list.
    """

    if isinstance(embedding, str):

        embedding = embedding.strip()

        embedding = embedding.strip("[]")

        return [
            float(value)
            for value in embedding.split(",")
        ]

    return list(embedding)


def discover_topics(
    document_id,
    number_of_topics=30
):
    """
    Group document chunks into semantic clusters.

    This stage does NOT call an LLM.
    """

    rows = get_document_embeddings(
        document_id
    )

    if not rows:
        return []

    embeddings = []

    valid_rows = []

    for row in rows:

        try:

            embedding = parse_embedding(
                row["embedding"]
            )

            embeddings.append(
                embedding
            )

            valid_rows.append(row)

        except Exception as error:

            print(
                f"Skipping chunk "
                f"{row['id']}: {error}"
            )

    if not embeddings:

        return []

    embeddings = np.array(
        embeddings,
        dtype=np.float32
    )

    # ---------------------------------------------
    # Keep number of clusters reasonable
    # ---------------------------------------------

    number_of_topics = min(
        number_of_topics,
        len(valid_rows)
    )

    print(
        f"Clustering {len(valid_rows)} chunks "
        f"into {number_of_topics} groups..."
    )

    # ---------------------------------------------
    # Local clustering
    # ---------------------------------------------

    from sklearn.cluster import MiniBatchKMeans

    model = MiniBatchKMeans(
        n_clusters=number_of_topics,
        random_state=42,
        batch_size=256,
        n_init=10
    )

    labels = model.fit_predict(
        embeddings
    )

    # ---------------------------------------------
    # Build clusters
    # ---------------------------------------------

    clusters = []

    for cluster_id in range(
        number_of_topics
    ):

        cluster_indices = np.where(
            labels == cluster_id
        )[0]

        if len(cluster_indices) == 0:
            continue

        centroid = model.cluster_centers_[
            cluster_id
        ]

        # -----------------------------------------
        # Find representative chunks
        # -----------------------------------------

        distances = []

        for index in cluster_indices:

            distance = np.linalg.norm(
                embeddings[index] - centroid
            )

            distances.append(
                (distance, index)
            )

        distances.sort(
            key=lambda item: item[0]
        )

        representative_indices = [
            index
            for _, index in distances[:5]
        ]

        cluster_chunks = []

        for index in cluster_indices:

            row = valid_rows[index]

            cluster_chunks.append(
                {
                    "id": row["id"],
                    "text": row["chunk_text"],
                    "page": row["page_number"]
                }
            )

        representative_chunks = []

        for index in representative_indices:

            row = valid_rows[index]

            representative_chunks.append(
                {
                    "id": row["id"],
                    "text": row["chunk_text"],
                    "page": row["page_number"]
                }
            )

        clusters.append(
            {
                "cluster_id": cluster_id,
                "chunk_count": len(
                    cluster_chunks
                ),
                "chunks": cluster_chunks,
                "representative_chunks":
                    representative_chunks
            }
        )

    return clusters
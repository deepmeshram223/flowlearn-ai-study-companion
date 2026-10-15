from sqlalchemy import text

from backend.database.connection import engine


def search_database(search_term):

    print("\n" + "=" * 80)
    print("SEARCH:", search_term)
    print("=" * 80)

    query = text("""
        SELECT
            page_number,
            chunk_text
        FROM document_chunks
        WHERE document_id = :document_id
        AND chunk_text ILIKE :search_term
        LIMIT 20;
    """)

    with engine.connect() as connection:

        results = connection.execute(
            query,
            {
                "document_id": 54,
                "search_term": f"%{search_term}%"
            }
        )

        rows = results.fetchall()

    print("MATCHES:", len(rows))

    for row in rows:

        print("\nPAGE:", row[0])

        print("-" * 80)

        print(row[1][:1500])


search_database("NDB")

search_database("non-directional beacon")

search_database("non directional beacon")
from sqlalchemy import text
from backend.database.connection import engine


query = text("""
    SELECT
        id,
        page_number,
        chunk_text
    FROM document_chunks
    WHERE document_id = 54
      AND chunk_text ILIKE '%NDB%'
    ORDER BY page_number;
""")


with engine.connect() as connection:
    results = connection.execute(query).mappings().all()


print("\nNDB MATCHING CHUNKS:", len(results))

for result in results:

    print("\n" + "=" * 100)

    print(
        f"CHUNK ID: {result['id']} | "
        f"PAGE: {result['page_number']}"
    )

    print("=" * 100)

    print(result["chunk_text"][:2000])
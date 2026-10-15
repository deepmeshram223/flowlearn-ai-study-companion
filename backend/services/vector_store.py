from sqlalchemy import text

from backend.database.connection import engine


# ----------------------------------------
# Save document
# ----------------------------------------

def save_document(filename, file_type):
    query = text("""
        INSERT INTO documents (
            filename,
            file_type
        )
        VALUES (
            :filename,
            :file_type
        )
        RETURNING id;
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {
                "filename": filename,
                "file_type": file_type
            }
        )

        document_id = result.scalar()

    return document_id


# ----------------------------------------
# Save single chunk
# ----------------------------------------

def save_chunk(
    document_id,
    chunk_text,
    page_number,
    embedding
):
    query = text("""
        INSERT INTO document_chunks
        (
            document_id,
            chunk_text,
            page_number,
            embedding
        )
        VALUES
        (
            :document_id,
            :chunk_text,
            :page_number,
            :embedding
        )
        RETURNING id;
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {
                "document_id": document_id,
                "chunk_text": chunk_text,
                "page_number": page_number,
                "embedding": embedding
            }
        )

        chunk_id = result.scalar()

    return chunk_id


# ----------------------------------------
# Save chunks in batch
# ----------------------------------------

def save_chunks_batch(document_id, chunks, embeddings):
    """
    Save multiple chunks and embeddings
    in one database transaction.
    """

    if not chunks:
        return

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Number of chunks must match number of embeddings."
        )

    query = text("""
        INSERT INTO document_chunks
        (
            document_id,
            chunk_text,
            page_number,
            embedding
        )
        VALUES
        (
            :document_id,
            :chunk_text,
            :page_number,
            :embedding
        )
    """)

    records = []

    for chunk, embedding in zip(chunks, embeddings):
        records.append({
            "document_id": document_id,
            "chunk_text": chunk["text"],
            "page_number": chunk["page"],
            "embedding": embedding
        })

    with engine.begin() as connection:
        connection.execute(query, records)


# ----------------------------------------
# Search all documents
# ----------------------------------------

def search_similar_chunks(
    query_embedding,
    limit=5
):
    query = text("""
        SELECT
            dc.id,
            dc.document_id,
            d.filename,
            dc.chunk_text,
            dc.page_number,
            dc.embedding <=> CAST(:query_embedding AS vector)
                AS distance
        FROM document_chunks dc
        JOIN documents d
            ON dc.document_id = d.id
        ORDER BY dc.embedding <=> CAST(:query_embedding AS vector)
        LIMIT :limit;
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "query_embedding": str(query_embedding),
                "limit": limit
            }
        )

        rows = result.mappings().all()

    return rows


# ----------------------------------------
# Hybrid search inside one document
# ----------------------------------------

# ----------------------------------------
# Hybrid search inside one document
# ----------------------------------------

def search_similar_chunks_for_document(
    query_embedding,
    document_id,
    limit=5,
    search_terms=None
):
    """
    Balanced hybrid retrieval.

    Combines:
    - semantic/vector search
    - keyword search
    - term importance
    - balanced topic selection
    """

    import math

    # --------------------------------------------------
    # 1. VECTOR SEARCH
    # --------------------------------------------------

    vector_limit = max(limit * 4, 20)

    vector_query = text("""
        SELECT
            dc.id,
            dc.document_id,
            d.filename,
            dc.chunk_text,
            dc.page_number,
            dc.embedding <=> CAST(:query_embedding AS vector)
                AS distance
        FROM document_chunks dc
        JOIN documents d
            ON dc.document_id = d.id
        WHERE dc.document_id = :document_id
        ORDER BY dc.embedding <=> CAST(:query_embedding AS vector)
        LIMIT :limit;
    """)

    with engine.connect() as connection:

        result = connection.execute(
            vector_query,
            {
                "query_embedding": str(query_embedding),
                "document_id": document_id,
                "limit": vector_limit
            }
        )

        vector_rows = result.mappings().all()

    # --------------------------------------------------
    # 2. CLEAN SEARCH TERMS
    # --------------------------------------------------

    stop_words = {
        "and",
        "or",
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "of",
        "to",
        "in",
        "on",
        "for",
        "from",
        "with",
        "about",
        "their",
        "them",
        "this",
        "that",
        "these",
        "those",
        "what",
        "which",
        "who",
        "how",
        "why",
        "does",
        "do",
        "can",
        "could",
        "would",
        "please",
        "me",
        "give",
        "tell",
        "explain"
    }

    valid_terms = []

    for term in (search_terms or []):

        term = term.strip().lower()

        if not term:
            continue

        if len(term) < 2:
            continue

        if term in stop_words:
            continue

        if term not in valid_terms:
            valid_terms.append(term)

    if not valid_terms:
        return vector_rows[:limit]

    # --------------------------------------------------
    # 3. CALCULATE TERM IMPORTANCE
    # --------------------------------------------------

    total_query = text("""
        SELECT COUNT(*)
        FROM document_chunks
        WHERE document_id = :document_id;
    """)

    with engine.connect() as connection:

        total_result = connection.execute(
            total_query,
            {
                "document_id": document_id
            }
        )

        total_chunks = total_result.scalar() or 1

    term_importance = {}

    count_query = text("""
        SELECT COUNT(*)
        FROM document_chunks
        WHERE document_id = :document_id
          AND chunk_text ILIKE :search_term;
    """)

    with engine.connect() as connection:

        for term in valid_terms:

            count_result = connection.execute(
                count_query,
                {
                    "document_id": document_id,
                    "search_term": f"%{term}%"
                }
            )

            match_count = count_result.scalar() or 0

            # Rare terms are more important than
            # extremely common terms.
            idf = math.log(
                (total_chunks + 1) /
                (match_count + 1)
            ) + 1

            # Give important aviation abbreviations
            # extra priority.
            if term in {
                "ndb",
                "vor",
                "ils",
                "gnss",
                "rnav",
                "pbn",
                "adsb",
                "mlat",
                "tcas"
            }:
                idf += 5

            term_importance[term] = idf

    # --------------------------------------------------
    # 4. SELECT IMPORTANT TERMS
    # --------------------------------------------------

    important_terms = sorted(
        valid_terms,
        key=lambda term: term_importance[term],
        reverse=True
    )

    # We don't want generic words to dominate.
    #
    # Two strongest concepts are enough for the
    # current study-question use case.
    important_terms = important_terms[:2]

    print("\nImportant retrieval terms:")

    for term in important_terms:
        print(
            f"  {term}: "
            f"{term_importance[term]:.2f}"
        )

    # --------------------------------------------------
    # 5. SEARCH EACH IMPORTANT TERM
    # --------------------------------------------------

    candidates_by_term = {}

    keyword_limit = max(limit * 2, 10)

    keyword_query = text("""
        SELECT
            dc.id,
            dc.document_id,
            d.filename,
            dc.chunk_text,
            dc.page_number,
            dc.embedding <=> CAST(:query_embedding AS vector)
                AS distance
        FROM document_chunks dc
        JOIN documents d
            ON dc.document_id = d.id
        WHERE dc.document_id = :document_id
          AND dc.chunk_text ILIKE :search_term
        ORDER BY
            dc.embedding <=> CAST(:query_embedding AS vector)
        LIMIT :limit;
    """)

    with engine.connect() as connection:

        for term in important_terms:

            result = connection.execute(
                keyword_query,
                {
                    "query_embedding": str(query_embedding),
                    "document_id": document_id,
                    "search_term": f"%{term}%",
                    "limit": keyword_limit
                }
            )

            candidates_by_term[term] = [
                {
                    **dict(row),
                    "matched_term": term,
                    "keyword_score": term_importance[term]
                }
                for row in result.mappings().all()
            ]

    # --------------------------------------------------
    # 6. BALANCED SELECTION
    # --------------------------------------------------

    selected = []
    selected_ids = set()

    if len(important_terms) == 1:

        per_term_limit = limit

    else:

        # Divide available slots between concepts.
        per_term_limit = max(
            1,
            limit // len(important_terms)
        )

    # Example with limit=5 and two topics:
    #
    # Topic A -> 2 results
    # Topic B -> 2 results
    # Vector  -> 1 result

    for term in important_terms:

        candidates = candidates_by_term.get(
            term,
            []
        )

        added = 0

        for candidate in candidates:

            if candidate["id"] in selected_ids:
                continue

            selected.append(candidate)

            selected_ids.add(candidate["id"])

            added += 1

            if added >= per_term_limit:
                break

            if len(selected) >= limit:
                break

        if len(selected) >= limit:
            break

    # --------------------------------------------------
    # 7. FILL REMAINING SLOTS WITH VECTOR RESULTS
    # --------------------------------------------------

    for row in vector_rows:

        if row["id"] in selected_ids:
            continue

        selected.append(
            {
                **dict(row),
                "keyword_score": 0,
                "matched_term": None
            }
        )

        selected_ids.add(row["id"])

        if len(selected) >= limit:
            break

    # --------------------------------------------------
    # 8. FINAL RESULT
    # --------------------------------------------------

    return selected[:limit]
# ----------------------------------------
# Get all chunks from one document
# ----------------------------------------

def get_document_chunks(document_id):
    query = text("""
        SELECT
            dc.id,
            dc.document_id,
            d.filename,
            dc.chunk_text,
            dc.page_number
        FROM document_chunks dc
        JOIN documents d
            ON dc.document_id = d.id
        WHERE dc.document_id = :document_id
        ORDER BY dc.id;
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "document_id": document_id
            }
        )

        rows = result.mappings().all()

    return rows

# ----------------------------------------
# Update document processing status
# ----------------------------------------

def update_document_status(
    document_id,
    status=None,
    total_chunks=None,
    processed_chunks=None,
    error_message=None,
    processing_stage=None,
    current_page=None,
    total_pages=None
):
    query = text("""
        UPDATE documents
        SET
            status = COALESCE(:status, status),
            total_chunks = COALESCE(:total_chunks, total_chunks),
            processed_chunks = COALESCE(
                :processed_chunks,
                processed_chunks
            ),
            error_message = :error_message,
            processing_stage = COALESCE(
                :processing_stage,
                processing_stage
            ),
            current_page = COALESCE(
                :current_page,
                current_page
            ),
            total_pages = COALESCE(
                :total_pages,
                total_pages
            )
        WHERE id = :document_id;
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "document_id": document_id,
                "status": status,
                "total_chunks": total_chunks,
                "processed_chunks": processed_chunks,
                "error_message": error_message,
                "processing_stage": processing_stage,
                "current_page": current_page,
                "total_pages": total_pages
            }
        )
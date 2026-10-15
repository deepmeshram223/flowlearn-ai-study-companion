from backend.services.embeddings import generate_embedding

from backend.services.vector_store import (
    search_similar_chunks,
    search_similar_chunks_for_document,
    get_document_chunks
)

from backend.services.llm import generate_answer


# ----------------------------------------
# Extract useful search terms
# ----------------------------------------

def extract_search_terms(question):
    """
    Extract useful keywords from the user's question.

    Keeps important technical terms while removing
    common question words.
    """

    stop_words = {
        "what",
        "what's",
        "whats",
        "is",
        "are",
        "was",
        "were",
        "the",
        "a",
        "an",
        "and",
        "or",
        "of",
        "to",
        "in",
        "on",
        "for",
        "from",
        "with",
        "about",
        "tell",
        "me",
        "give",
        "explain",
        "describe",
        "how",
        "why",
        "does",
        "do",
        "can",
        "could",
        "would",
        "please",
        "also",
        "information",
        "details",
        "detail",
        "their",
        "them",
        "they",
        "this",
        "that",
        "these",
        "those",        
    }

    # Keep punctuation-free words
    words = question.lower().replace(",", " ").replace(
        ".", " "
    ).replace("?", " ").replace(
        "!", " "
    ).replace(":", " ").replace(
        ";", " "
    ).split()

    terms = []

    for word in words:
        word = word.strip()

        if not word:
            continue

        if word in stop_words:
            continue

        if len(word) < 2:
            continue

        if word not in terms:
            terms.append(word)

    return terms


# ----------------------------------------
# Retrieve relevant context
# ----------------------------------------

def retrieve_context(question, document_id=None, limit=5):

    query_embedding = generate_embedding(question)

    search_terms = extract_search_terms(question)

    print("\nSearch terms:", search_terms)

    if document_id is not None:

        results = search_similar_chunks_for_document(
            query_embedding=query_embedding,
            document_id=document_id,
            limit=limit,
            search_terms=search_terms
        )

    else:

        results = search_similar_chunks(
            query_embedding,
            limit
        )

    return results


# ----------------------------------------
# Build context for LLM
# ----------------------------------------

def build_context(results):

    context_parts = []

    for result in results:

        context_parts.append(
            f"[Page {result['page_number']}]\n"
            f"{result['chunk_text']}"
        )

    return "\n\n".join(context_parts)


# ----------------------------------------
# Answer question
# ----------------------------------------

def answer_question(
    question,
    document_id=None,
    limit=5
):

    results = retrieve_context(
        question,
        document_id=document_id,
        limit=limit
    )

    context = build_context(results)

    prompt = f"""
You are an AI study assistant.

Answer the user's question using ONLY the information
provided in the context below.

If the answer cannot be found in the context, say:

"I couldn't find this information in the uploaded study material."

Do not invent facts.
Do not use outside knowledge.

Context:
--------------------
{context}
--------------------

Question:
{question}

Answer the question accurately using the provided context.

If the question asks for:
- roles
- responsibilities
- features
- requirements
- steps
- categories
- names
- multiple items

make sure to include ALL relevant items supported by the context.

Do not stop after finding the first matching item.

If multiple relevant items appear in different parts of the context,
combine them into one complete answer.

Do not invent missing information.

FORMATTING RULES:

- Do NOT use Markdown.
- Do NOT use asterisks (*) anywhere.
- Do NOT use double asterisks (**).
- Do NOT use Markdown headings such as # or ##.
- Do NOT use Markdown bullet points.
- Do NOT use backticks.
- Do NOT use decorative symbols.
- For lists, use simple numbered lists:
  1. First item
  2. Second item
  3. Third item
- Use plain text only.
- Use short paragraphs when a list is not necessary.
- Keep the answer clear, readable and concise.
"""

    answer = generate_answer(prompt)

    # ------------------------------------
    # Build unique sources
    # ------------------------------------

    sources = []

    for result in results:

        source = {
            "document_id": result["document_id"],
            "filename": result["filename"],
            "page_number": result["page_number"],
            "distance": result["distance"]
        }

        if source not in sources:
            sources.append(source)

    return {
        "answer": answer,
        "sources": sources
    }
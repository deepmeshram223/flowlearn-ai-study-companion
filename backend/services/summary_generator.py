import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.rag import answer_question


def generate_document_summary(document_id):
    """
    Generate a concise AI summary of the uploaded document.
    """

    summary_question = """
Summarize the uploaded study material concisely.

Use ONLY the uploaded study material.

Give the output in exactly this format:

## Quick Summary
Give 5-8 important points from the document.

## Key Concepts
List the 5-10 most important concepts.
For each concept, give only 1-2 sentences explaining it.

## Remember
Give 5 short exam-focused points to remember.

Rules:
- Keep the entire summary short.
- Do not write long paragraphs.
- Do not repeat information.
- Do not include unnecessary examples.
- Do not invent information.
- Prefer bullet points.
- Aim for approximately 400-600 words maximum.
"""

    result = answer_question(
        summary_question,
        document_id=document_id,
        limit=5
    )

    return {
        "summary": result["answer"],
        "sources": result["sources"]
    }
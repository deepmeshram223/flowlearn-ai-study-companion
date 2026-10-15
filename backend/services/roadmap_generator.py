import json
import re

from backend.services.llm import generate_roadmap_answer


def clean_json_response(response):
    response = response.strip()

    response = re.sub(
        r"^```(?:json)?\s*",
        "",
        response,
        flags=re.IGNORECASE
    )

    response = re.sub(
        r"\s*```$",
        "",
        response
    )

    start = response.find("{")
    end = response.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "LLM did not return a JSON object."
        )

    return response[start:end + 1]


def generate_roadmap(document_text):

    # --------------------------------------------------
    # STAGE 1: Extract topics from the study material
    # --------------------------------------------------

    chunks = document_text.split("\n\n")

    batch_size = 20

    topic_summaries = []

    for i in range(0, len(chunks), batch_size):

        batch = chunks[i:i + batch_size]

        batch_text = "\n\n".join(batch)

        prompt = f"""
You are extracting learning topics from study material.

Your ONLY task is to identify important topics.

RETURN ONLY THIS JSON OBJECT:

{{
  "topics": [
    {{
      "title": "Topic name",
      "description": "Short description",
      "source_pages": [1]
    }}
  ]
}}

IMPORTANT:

Return JSON directly.

Do NOT write:
- explanations
- introductions
- conclusions
- markdown
- code fences
- comments

The first character of your response must be {{
and the last character must be }}.

RULES:

1. Only use information present in the study material.
2. Do not use outside knowledge.
3. Do not invent topics.
4. Avoid duplicate topics.
5. Each topic must represent something a student should learn.
6. Keep descriptions under 15 words.
7. source_pages must contain page numbers appearing in the material.
8. Return between 3 and 10 topics.
9. Use double quotes for all JSON strings.

STUDY MATERIAL:

{batch_text}
"""

        response = generate_roadmap_answer(prompt)

        try:

            cleaned = clean_json_response(response)

            result = json.loads(cleaned)

            topic_summaries.extend(
                result.get("topics", [])
            )

        except Exception as error:

            print(
                f"Warning: topic extraction failed "
                f"for batch {i // batch_size + 1}: {error}"
            )

            print("Model response:")
            print(response)

            continue

    # --------------------------------------------------
    # Check whether topics were extracted
    # --------------------------------------------------

    if not topic_summaries:

        raise ValueError(
            "No learning topics could be extracted from the study material."
        )

    print(
        f"Extracted {len(topic_summaries)} topics "
        f"from the study material."
    )

    # --------------------------------------------------
    # STAGE 2: Generate final roadmap
    # --------------------------------------------------

    topics_text = "\n\n".join(
        f"""
Topic: {topic.get("title", "")}
Description: {topic.get("description", "")}
Pages: {topic.get("source_pages", [])}
"""
        for topic in topic_summaries
    )

    final_prompt = f"""
Create a learning roadmap from the extracted topics below.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "title": "Roadmap title",
  "description": "Short description",
  "phases": [
    {{
      "id": "phase_1",
      "title": "Phase title",
      "nodes": [
        {{
          "id": "n1",
          "title": "Topic",
          "description": "Short description",
          "difficulty": "beginner",
          "estimated_minutes": 30,
          "prerequisites": [],
          "source_pages": [],
          "checkpoint": false
        }}
      ]
    }}
  ],
  "connections": [
    {{
      "from": "n1",
      "to": "n2"
    }}
  ]
}}

STRICT RULES:

- Valid JSON only.
- No markdown.
- No explanations.
- Exactly 3 phases.
- Exactly 3 nodes per phase.
- Exactly 9 nodes total.
- Node IDs must be n1 through n9.
- At most 8 connections.
- Use only topics supported by the extracted material.
- Do not invent topics.
- Arrange topics from foundational to advanced.
- Each node must represent one meaningful learning topic.
- prerequisites may only contain existing node IDs.
- source_pages must contain only pages from the extracted topics.
- estimated_minutes must be an integer.
- Keep descriptions under 15 words.

EXTRACTED TOPICS:

{topics_text}
"""

    response = generate_roadmap_answer(
        final_prompt
    )

    try:

        cleaned = clean_json_response(response)

        return json.loads(cleaned)

    except json.JSONDecodeError:

        print(
            "Final roadmap JSON was malformed."
        )

        repair_prompt = f"""
Fix the following malformed JSON.

Return ONLY valid JSON.

Do not explain anything.
Do not use markdown.
Do not change the information.
Only repair the JSON syntax.

MALFORMED JSON:

{cleaned}
"""

        repaired = generate_roadmap_answer(
            repair_prompt
        )

        repaired = clean_json_response(
            repaired
        )

        try:

            return json.loads(
                repaired
            )

        except json.JSONDecodeError as error:

            print(
                "\n===== ROADMAP JSON FAILED ====="
            )

            print(repaired)

            print(
                "\n===== JSON ERROR ====="
            )

            print(error)

            raise ValueError(
                "The AI could not produce valid roadmap JSON."
            )
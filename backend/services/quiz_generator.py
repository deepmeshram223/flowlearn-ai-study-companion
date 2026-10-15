import json
import re

from backend.services.rag import answer_question


def _extract_json(text):
    """Extract a JSON object even if the model wraps it in markdown or extra text."""
    cleaned = re.sub(r"```(?:json)?", "", text or "", flags=re.IGNORECASE).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object was found in the AI response.")

    return json.loads(cleaned[start:end + 1])


def _validate_quiz(quiz_data):
    """Validate the quiz structure expected by the frontend."""
    if not isinstance(quiz_data, dict):
        raise ValueError("Quiz response is not a JSON object.")

    questions = quiz_data.get("questions")

    if not isinstance(questions, list) or len(questions) != 5:
        raise ValueError("Quiz must contain exactly 5 questions.")

    for index, question in enumerate(questions, start=1):
        if not isinstance(question, dict):
            raise ValueError(f"Question {index} is invalid.")

        question_text = question.get("question")
        options = question.get("options")
        answer = question.get("answer")
        explanation = question.get("explanation")

        if not isinstance(question_text, str) or not question_text.strip():
            raise ValueError(f"Question {index} has no valid question text.")

        if (
            not isinstance(options, list)
            or len(options) != 4
            or any(not isinstance(option, str) or not option.strip() for option in options)
            or len(set(options)) != 4
        ):
            raise ValueError(f"Question {index} must have 4 unique options.")

        if not isinstance(answer, str) or answer not in options:
            raise ValueError(
                f"Question {index} has a correct answer that is not one of its options."
            )

        if not isinstance(explanation, str) or not explanation.strip():
            raise ValueError(f"Question {index} has no valid explanation.")

    return quiz_data


def _build_quiz_prompt(topic_title, topic_description):
    return f"""
Create a 5-question multiple-choice quiz about the topic "{topic_title}".

Use ONLY the uploaded study material.

Topic description:
{topic_description}

For each question provide:
- question
- exactly 4 unique options
- correct answer (must exactly match one option)
- short explanation

Return ONLY valid JSON in this exact format:

{{
    "questions": [
        {{
            "question": "Question text",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "answer": "Option A",
            "explanation": "Why this answer is correct."
        }}
    ]
}}

Create exactly 5 questions.
"""


def generate_topic_quiz(document_id, topic_title, topic_description=""):
    """
    Generate and validate a topic quiz using only the uploaded study material.

    Returns:
        dict: Validated quiz data with exactly five questions.
    """
    prompt = _build_quiz_prompt(topic_title, topic_description)

    first_result = answer_question(
        prompt,
        document_id=document_id,
        limit=5
    )

    raw_response = first_result.get("answer", "")

    try:
        quiz_data = _extract_json(raw_response)
        return _validate_quiz(quiz_data)
    except (ValueError, json.JSONDecodeError):
        # One repair attempt keeps the UI simple while handling occasional
        # markdown/formatting mistakes from the LLM.
        repair_prompt = f"""
Convert the following quiz into valid JSON.

Requirements:
- exactly 5 questions
- every question has exactly 4 unique options
- "answer" must exactly match one of the options
- every question must have an explanation
- return ONLY JSON
- do not add markdown or extra text

Expected format:
{{
    "questions": [
        {{
            "question": "Question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Option A",
            "explanation": "Why this answer is correct."
        }}
    ]
}}

Quiz to repair:
{raw_response}
"""

        repaired_result = answer_question(
            repair_prompt,
            document_id=document_id,
            limit=5
        )

        repaired_data = _extract_json(
            repaired_result.get("answer", "")
        )

        return _validate_quiz(repaired_data)

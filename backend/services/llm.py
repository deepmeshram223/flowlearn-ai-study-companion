import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
GROQ_ROADMAP_MODEL = os.getenv("GROQ_ROADMAP_MODEL")


if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in .env")

if not GROQ_MODEL:
    raise ValueError("GROQ_MODEL is not set in .env")

if not GROQ_ROADMAP_MODEL:
    raise ValueError("GROQ_ROADMAP_MODEL is not set in .env")


client = Groq(api_key=GROQ_API_KEY)


def generate_answer(prompt):
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


def generate_roadmap_answer(prompt):
    response = client.chat.completions.create(
        model=GROQ_ROADMAP_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=8000
    )

    choice = response.choices[0]

    print("\n===== ROADMAP MODEL DEBUG =====")
    print("Finish reason:", choice.finish_reason)
    print("Usage:", getattr(response, "usage", None))
    print("Content length:", len(choice.message.content or ""))
    print("===============================\n")

    return choice.message.content or ""
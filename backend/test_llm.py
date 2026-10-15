from backend.services.llm import generate_answer


prompt = """
Explain what an operating system is in simple terms.
Keep the answer under 100 words.
"""


answer = generate_answer(prompt)


print("\nLLM Response:\n")
print(answer)
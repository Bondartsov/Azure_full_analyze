from core.ai.code_advisor import query_openai

def analyze_structure(code: str) -> str:
    """
    Анализирует структуру кода.
    """
    prompt = f"Опиши структуру этого кода:\n\n{code}"
    return query_openai(prompt)

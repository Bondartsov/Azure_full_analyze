# tests/test_openai_connection.py
import pytest
from core.ai.code_advisor import query_openai
from core.logging.logger import log

def test_query_openai():
    prompt = """
    Проанализируй следующий код:

    def add(a, b):
        # Функция для сложения двух чисел
        return a + b

    1. Определи структуру кода.
    2. Объясни, что делает этот код.
    3. Найди возможные ошибки или улучшения.
    4. Насколько сложен этот код (1-10)?
    """
    
    analysis = query_openai(prompt)
    print("Анализ от OpenAI:")
    print(analysis)

    assert isinstance(analysis, str), "Анализ должен быть строкой"
    assert len(analysis) > 0, "Анализ не должен быть пустым"
    
    if analysis:
        log("✅ Тестовый анализ успешно получен от OpenAI.")
    else:
        log("⚠️ Не удалось получить анализ от OpenAI.", level="WARNING")
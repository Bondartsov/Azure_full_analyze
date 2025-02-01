# tests/manual_test_query.py

import sys
import os

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai.code_advisor import query_openai
from core.logging.logger import log

def manual_test_query():
    prompt = """
    Проанализируй следующий код:

    def greet(name):
        # Функция приветствия
        print(f"Hello, {name}!")

    1. Определи структуру кода.
    2. Объясни, что делает этот код.
    3. Найди возможные ошибки или улучшения.
    4. Насколько сложен этот код (1-10)?
    """

    # Получаем имя модели из переменных окружения
    OPENAI_MODEL = os.getenv("OPENAI_MODEL")
    log(f"🔍 Тестовый запрос к модели: {OPENAI_MODEL}")
    print(f"🔍 Тестовый запрос к модели: {OPENAI_MODEL}")

    # Отправляем запрос к OpenAI
    analysis = query_openai(prompt)
    print("Анализ от OpenAI:")
    print(analysis)

    # Проверяем корректность ответа
    assert isinstance(analysis, str), "Анализ должен быть строкой"
    assert len(analysis) > 0, "Анализ не должен быть пустым"
    
    if analysis:
        log("✅ Ручной тест: Анализ успешно получен от OpenAI.")
        log(f"✅ Модель {OPENAI_MODEL} успешно ответила.")
        print(f"✅ Модель {OPENAI_MODEL} успешно ответила.")
    else:
        log("⚠️ Ручной тест: Не удалось получить анализ от OpenAI.", level="WARNING")
        print("⚠️ Ручной тест: Не удалось получить анализ от OpenAI.")

if __name__ == "__main__":
    manual_test_query()
# tests/manual_test_query.py

import sys
import os

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logging.logger import setup_logging  # Импорт функции настройки логирования
setup_logging()  # Инициализация логирования

from core.ai.report_generator import generate_ai_report
from core.logging.logger import log  # Импорт функции log после инициализации логирования

def manual_test_query():
    # Определение mock_analysis
    mock_analysis = {
        "project": "TestProject",
        "repository": "ST.CPM",
        "folder": "TestFolder",
        "file": "test_file.py",
        "content": "print('Hello, World!')"
    }

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
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "cl100k_base")
    log(f"🔍 Тестовый запрос к модели: {OPENAI_MODEL}")
    print(f"🔍 Тестовый запрос к модели: {OPENAI_MODEL}")

    # Отправляем запрос к OpenAI через генерацию отчёта
    report_path = generate_ai_report(
        mock_analysis["project"],
        mock_analysis["repository"],
        mock_analysis["folder"],
        mock_analysis["file"],
        mock_analysis["content"]
    )
    print("Анализ от OpenAI:")
    print(report_path)

    # Проверяем корректность создания отчёта
    assert report_path is not None, "Отчёт не был создан."
    assert os.path.exists(report_path), f"Отчёт не найден по пути: {report_path}"
    
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "📌 **Анализ кода:**" in content, "Секция анализа отсутствует в отчёте."
        assert "Hello, World!" in content, "Анализ не содержит ожидаемых данных."
    
    log("✅ Ручной тест: Анализ успешно получен от OpenAI.")
    log(f"✅ Модель {OPENAI_MODEL} успешно ответила.")
    print(f"✅ Модель {OPENAI_MODEL} успешно ответила.")

if __name__ == "__main__":
    manual_test_query()
# tests/manual_test_report_generator.py

import sys
import os

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logging.logger import setup_logging, log
from core.ai.report_generator import generate_ai_report

def manual_test_generate_ai_report():
    setup_logging()
    log("🔧 Настройка логирования для ручного теста генерации отчёта.")
    
    project_name = "ManualTestProject"
    repository_name = "TestRepo"
    folder_name = "TestFolder"
    file_name = "manual_test_file.py"
    file_content = "def hello():\n    print('Hello, Manual Testing!')"
    
    report_path = generate_ai_report(
        project_name,
        repository_name,
        folder_name,
        file_name,
        file_content
    )
    
    assert report_path is not None, "Отчёт не был создан."
    assert os.path.exists(report_path), f"Отчёт не найден по пути: {report_path}"
    
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "📌 **Анализ кода:**" in content, "Секция анализа отсутствует в отчёте."
        assert "Hello, Manual Testing!" in content, "Анализ не содержит ожидаемых данных."
    
    log(f"✅ Ручной тест генерации отчёта прошёл успешно. Отчёт создан: {report_path}")
    print(f"✅ Ручной тест генерации отчёта прошёл успешно. Отчёт создан: {report_path}")

if __name__ == "__main__":
    manual_test_generate_ai_report()
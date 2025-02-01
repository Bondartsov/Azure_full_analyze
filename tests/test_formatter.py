import pytest
from core.reports.report_formatter import format_repository_report, format_project_summary

@pytest.fixture
def test_repository_data():
    """Тестовые данные для отчёта о репозитории."""
    return [
        {"path": "main.py", "name": "main.py", "role": "Код", "lines": 100, "comments": 10, "tokens": 500},
        {"path": "utils/helpers.py", "name": "helpers.py", "role": "Утилиты", "lines": 50, "comments": 5, "tokens": 250},
        {"path": "README.md", "name": "README.md", "role": "Документация", "lines": 20, "comments": 0, "tokens": 100},
    ]

def test_format_repository_report(test_repository_data):
    """Проверяет форматирование отчёта по репозиторию."""
    project_name = "TestProject"
    repository_name = "TestRepo"

    report = format_repository_report(project_name, repository_name, test_repository_data)

    assert repository_name in report, "Название репозитория отсутствует в отчёте!"
    assert "📂 Корневая директория" in report, "Корневая директория не отображается!"
    assert "📄 main.py" in report, "Файл main.py отсутствует в отчёте!"
    assert "📄 utils/helpers.py" in report, "Файл utils/helpers.py отсутствует в отчёте!"
    assert "🔢 100 строк" in report, "Количество строк для main.py отсутствует!"

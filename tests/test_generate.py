import os
import pytest
from core.reports.generate import generate_report

@pytest.fixture
def test_repository_data():
    """Тестовые данные для генерации отчёта."""
    return [
        {"path": "main.py", "role": "Код", "lines": 100, "comments": 10, "tokens": 500},
        {"path": "utils/helpers.py", "role": "Код", "lines": 50, "comments": 5, "tokens": 250},
        {"path": "README.md", "role": "Документация", "lines": 20, "comments": 0, "tokens": 100},
    ]

def test_generate_report(test_repository_data):
    """Проверяет генерацию отчёта по репозиторию."""
    project_name = "TestProject"
    repository_name = "TestRepo"

    report_path = generate_report(project_name, repository_name, test_repository_data)

    assert os.path.exists(report_path), "Файл отчёта не был создан!"

    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert project_name in content, "Название проекта отсутствует в отчёте!"
        assert repository_name in content, "Название репозитория отсутствует в отчёте!"
        assert "📄 main.py" in content, "Файл main.py отсутствует в отчёте!"

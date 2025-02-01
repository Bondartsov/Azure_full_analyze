import os
import pytest
from core.reports.summary import generate_summary

@pytest.fixture
def test_repositories():
    """Создаёт тестовые данные о репозиториях."""
    return [
        {
            "repository": "Repo1",
            "tokens": 600,
            "files": [
                {"path": "main.py", "role": "Код", "lines": 100, "comments": 10, "tokens": 500},
                {"path": "utils/helpers.py", "role": "Код", "lines": 20, "comments": 5, "tokens": 100}
            ]
        },
        {
            "repository": "Repo2",
            "tokens": 1500,
            "files": [
                {"path": "server/main.py", "role": "Код", "lines": 300, "comments": 30, "tokens": 1500}
            ]
        }
    ]

def test_generate_summary(test_repositories):
    """Проверяет генерацию сводного отчёта по проекту."""
    project_name = "TestProject"

    report_path = generate_summary(project_name, test_repositories)

    # Проверяем, что отчёт создан
    assert os.path.exists(report_path), "Файл сводного отчёта не был создан!"

    # Проверяем, что файл не пустой
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert project_name in content, "Название проекта отсутствует в отчёте!"
        assert "Repo1" in content, "Репозиторий Repo1 отсутствует в отчёте!"
        assert "Repo2" in content, "Репозиторий Repo2 отсутствует в отчёте!"
        assert "120 строк" in content, "Количество строк для Repo1 отсутствует!"
        assert "300 строк" in content, "Количество строк для Repo2 отсутствует!"

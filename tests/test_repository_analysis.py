# tests/test_repository_analysis.py
import os
import tempfile
import pytest

# Импортируем тестируемые функции
from core.analyze.repository_analysis import analyze_repository_fast, analyze_repository_deep

# Определяем фиктивные (dummy) реализации зависимых функций:

def dummy_count_tokens_in_repo(project_name, repository_name):
    """
    Функция возвращает фиктивное значение:
    - files_data: список словарей, где для каждого файла указан его путь, имя и содержимое.
    - total_tokens: общее число токенов.
    """
    files_data = [
        {"file_name": "test1.py", "folder": "src", "content": "print('Hello World')"}
    ]
    total_tokens = 42
    return files_data, total_tokens

def dummy_generate_report(project_name, repository_name, files_data):
    """
    Функция генерирует фиктивный отчёт (быстрый анализ) в системной временной папке и возвращает его путь.
    """
    tmp_dir = tempfile.gettempdir()
    report_path = os.path.join(tmp_dir, f"report_{repository_name}.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("Dummy fast report")
    return report_path

def dummy_generate_deep_report_for_repo(project_name, repository_name, files_data):
    """
    Функция генерирует фиктивный отчёт глубокого анализа и возвращает его путь.
    """
    tmp_dir = tempfile.gettempdir()
    report_path = os.path.join(tmp_dir, f"deep_report_{repository_name}.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("Dummy deep report")
    return report_path

def dummy_get_deep_reports_for_repo(project_name, repository_name, files_data):
    """
    Возвращает список фиктивных путей к ИИ‑отчётам для каждого файла.
    """
    return [f"/dummy/path/{file_data['file_name']}_ai.txt" for file_data in files_data]

def dummy_save_repo_data_to_cache(project_name, repository_name, total_tokens, files_data):
    """
    Фиктивная функция сохранения данных в кэш. Просто ничего не делает.
    """
    pass

@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    """
    Патчим зависимости в модуле repository_analysis.
    """
    monkeypatch.setattr(
        "core.analyze.repository_analysis.count_tokens_in_repo",
        dummy_count_tokens_in_repo
    )
    monkeypatch.setattr(
        "core.analyze.repository_analysis.generate_report",
        dummy_generate_report
    )
    monkeypatch.setattr(
        "core.analyze.repository_analysis.generate_deep_report_for_repo",
        dummy_generate_deep_report_for_repo
    )
    monkeypatch.setattr(
        "core.analyze.repository_analysis.get_deep_reports_for_repo",
        dummy_get_deep_reports_for_repo
    )
    monkeypatch.setattr(
        "core.utils.cache.save_repo_data_to_cache",
        dummy_save_repo_data_to_cache
    )

def test_analyze_repository_fast():
    """
    Тест для быстрого анализа.
    Ожидается, что:
      - Функция возвращает словарь с ключами repository, tokens, cached, files, report_path.
      - Поле "cached" установлено в False (так как анализ выполняется "с нуля").
      - Используется фиктивная функция generate_report.
    """
    project_name = "TestProject"
    repository_name = "TestRepo"

    result = analyze_repository_fast(project_name, repository_name, repo_changed=True)
    
    assert result is not None, "Функция должна вернуть результат, а не None"
    assert result["repository"] == repository_name
    assert result["tokens"] == 42
    assert result["cached"] is False
    tmp_dir = tempfile.gettempdir()
    expected_report_path = os.path.join(tmp_dir, f"report_{repository_name}.txt")
    assert result["report_path"] == expected_report_path
    assert "ai_reports" not in result

import pytest
from core.analyze.repository_analysis import analyze_repository_deep

@pytest.fixture
def mock_fast_results():
    return {
        "repository": "TestRepo",
        "tokens": 42,
        "cached": False,
        "files": [
            {"file_name": "test_file.py", "folder": "TestFolder", "content": "print('Hello, World!')"}
        ],
        "report_path": "report_TestRepo.txt"
    }

def test_analyze_repository_deep(mock_fast_results):
    """
    Тест для глубокого анализа репозитория.
    Ожидается, что:
      - Функция возвращает список путей к ИИ-отчётам.
    """
    project_name = "TestProject"
    repository_name = "TestRepo"
    deep_reports = analyze_repository_deep(project_name, repository_name, mock_fast_results)
    
    assert isinstance(deep_reports, list), "Функция должна вернуть список"
    assert len(deep_reports) > 0, "Список ИИ-отчётов не должен быть пустым"
    for report_path in deep_reports:
        assert report_path.endswith(".txt"), "Каждый путь к отчёту должен заканчиваться на .txt"
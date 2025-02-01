# tests/test_report_generator.py

import pytest
import os
from core.ai.report_generator import generate_ai_report

@pytest.fixture
def mock_analysis():
    return {
        "project": "TestProject",
        "repository": "ST.CPM",
        "folder": "TestFolder",
        "file": "test_file.py",
        "content": "print('Hello, World!')"
    }

def test_generate_ai_report(mock_analysis):
    project_name = mock_analysis["project"]
    repository_name = mock_analysis["repository"]
    folder_name = mock_analysis["folder"]
    file_name = mock_analysis["file"]
    file_content = mock_analysis["content"]
    
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
        assert "Hello, World!" in content, "Анализ не содержит ожидаемых данных."

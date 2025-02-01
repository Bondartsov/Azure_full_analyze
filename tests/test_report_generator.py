import pytest
from core.ai.report_generator import generate_ai_report

@pytest.fixture
def mock_analysis():
    return {
        "project": "TestProject",
        "repository": "TestRepo",
        "folder": "TestFolder",
        "file": "test_file.py",
        "content": "print('Hello, World!')"
    }

def test_generate_ai_report(mock_analysis):
    report_path = generate_ai_report(
        mock_analysis["project"],
        mock_analysis["repository"],
        mock_analysis["folder"],
        mock_analysis["file"],
        mock_analysis["content"]
    )
    assert report_path.endswith(".txt")  # Проверяем, что файл сохранён

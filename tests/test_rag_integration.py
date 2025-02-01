import pytest
from core.ai.rag_manager import store_in_rag, query_rag

@pytest.fixture
def sample_text():
    return "This is a test document for RAG storage."

@pytest.fixture
def sample_query():
    return "What is the test document about?"

@pytest.fixture
def sample_metadata():
    return {
        "repository_name": "TestRepo",
        "folder_name": "TestFolder",
        "file_name": "test_file.py",
        "analysis": "This is a sample analysis"
    }

def test_store_in_rag(sample_text, sample_metadata):
    """
    Тест проверяет, что функция store_in_rag успешно загружает документ
    и возвращает True.
    """
    response = store_in_rag(
        sample_metadata["repository_name"],
        sample_metadata["folder_name"],
        sample_metadata["file_name"],
        sample_metadata["analysis"],  # Передаём анализ
        sample_text  # Передаём содержимое текста
    )
    assert response is True, "Функция store_in_rag должна возвращать True при успешной загрузке."

def test_query_rag(sample_query, sample_metadata):
    """
    Тест проверяет, что функция query_rag возвращает не None и тип результата - строка.
    """
    response = query_rag(
        "TestProject",  # Имя проекта
        sample_metadata["repository_name"],
        sample_metadata["folder_name"],
        sample_metadata["file_name"],
        sample_query
    )
    assert response is not None, "⚠️ query_rag() вернул None!"
    assert isinstance(response, str), "⚠️ query_rag() должен возвращать строку!"

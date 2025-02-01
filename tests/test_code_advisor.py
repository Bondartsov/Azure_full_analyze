import pytest
from core.ai.code_advisor import query_openai

@pytest.fixture
def test_prompt():
    return "Объясни, что делает этот код: print('Hello, World!')"

def test_query_openai(test_prompt):
    response = query_openai(test_prompt)
    assert isinstance(response, str)
    assert len(response) > 0

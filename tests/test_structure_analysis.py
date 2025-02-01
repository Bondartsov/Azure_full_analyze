import pytest
from core.ai.structure_analysis import analyze_structure

@pytest.fixture
def test_python_code():
    return """
    class Example:
        def method(self):
            pass
    """

def test_analyze_structure(test_python_code):
    response = analyze_structure(test_python_code.encode("utf-8").decode("utf-8"))
    assert isinstance(response, str)

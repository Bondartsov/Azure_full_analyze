# tests/test_token_counter.py

from core.utils.token_counter import count_tokens_in_text

def test_count_tokens():
    text = "print('Hello, World!')"
    tokens = count_tokens_in_text(text)
    assert isinstance(tokens, int), "Токены должны быть целым числом"
    assert tokens > 0, "Количество токенов должно быть положительным"

if __name__ == "__main__":
    test_count_tokens()
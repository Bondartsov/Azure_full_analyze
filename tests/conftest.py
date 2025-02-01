# tests/conftest.py

import os
import openai
from dotenv import load_dotenv
import pytest
from core.logging.logger import setup_logging

def clean_api_key(key: str) -> str:
    """
    Очищает API‑ключ:
      1. Убирает лишние пробелы и символ BOM.
      2. Если ключ обрамлён одинарными или двойными кавычками, удаляет их.
      3. Оставляет только символы из диапазона ASCII (код < 128).
    """
    key = key.strip().replace("\ufeff", "")
    # Если ключ начинается и заканчивается кавычками, удаляем их
    if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
        key = key[1:-1]
    # Оставляем только ASCII-символы
    key = "".join(c for c in key if ord(c) < 128)
    return key

# Загружаем переменные окружения из файла .env (укажите путь, если требуется)
load_dotenv(r"D:\Projects\Azure_full_analyze\.env")

# Получаем API‑ключ из переменной окружения
raw_api_key = os.getenv("OPENAI_API_KEY")
if raw_api_key is None:
    raise ValueError("Переменная OPENAI_API_KEY не найдена в файле .env")

# Очищаем API‑ключ
cleaned_key = clean_api_key(raw_api_key)

# Если после очистки остаются символы не из ASCII, выдаём ошибку
if any(ord(c) > 127 for c in cleaned_key):
    raise ValueError("API‑ключ содержит недопустимые символы. Проверьте, что он введён вручную без форматирования.")

# Обновляем переменную окружения, чтобы любые повторные чтения вернули очищённое значение
os.environ["OPENAI_API_KEY"] = cleaned_key

# Устанавливаем API‑ключ для клиента OpenAI
openai.api_key = cleaned_key
print("API‑ключ успешно загружен и очищен.")

@pytest.fixture(scope="session", autouse=True)
def initialize_logging():
    """
    Pytest fixture to initialize logging for the entire test session.
    This fixture is automatically used by all tests due to `autouse=True`.
    """
    setup_logging()
    print("Логирование успешно инициализировано.")
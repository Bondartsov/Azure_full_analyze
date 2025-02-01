import os
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv(r"D:\Projects\Azure_full_analyze\.env")

def clean_api_key(key: str) -> str:
    """
    Очищает API‑ключ:
      1. Убирает лишние пробелы и символ BOM.
      2. Если ключ обрамлён одинарными или двойными кавычками, удаляет их.
      3. Оставляет только символы из диапазона ASCII (код < 128).
    """
    key = key.strip().replace("\ufeff", "")
    if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
        key = key[1:-1]
    return "".join(c for c in key if ord(c) < 128)  # Оставляем только ASCII-символы

def test_api_key():
    # Получаем API‑ключ из переменной окружения
    raw_api_key = os.getenv("OPENAI_API_KEY")
    assert raw_api_key is not None, "Переменная OPENAI_API_KEY не найдена в файле .env"

    # Очищаем ключ от лишних символов (например, «умных» кавычек)
    api_key = clean_api_key(raw_api_key)
    assert all(ord(c) < 128 for c in api_key), "API‑ключ содержит недопустимые символы. Проверьте, что он введён без форматирования."

    # Создаём экземпляр клиента OpenAI
    client = OpenAI(api_key=api_key)

    # Пытаемся получить список моделей
    response = client.models.list()
    model_list = [model.id for model in response.data]  # Извлекаем идентификаторы моделей

    assert len(model_list) > 0, "Список моделей пуст или не получен"
    print("✅ Доступные модели:", model_list)

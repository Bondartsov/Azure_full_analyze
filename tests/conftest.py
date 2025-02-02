# tests/conftest.py

import os
import openai
from dotenv import load_dotenv
import pytest
from core.logging.logger import setup_logging
from core.utils.database import add_file_record, delete_file_record, create_connection, DB_PATH
import hashlib
import uuid

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
    Инициализирует систему логирования перед запуском тестов.
    """
    setup_logging()
    print("Логирование успешно инициализировано.")

@pytest.fixture
def setup_test_record():
    """
    Создаёт тестовую запись в базе данных для использования в тестах.
    
    Возвращает:
        tuple: Содержит ID созданной записи и путь к файлу.
    """
    project_name = "TestProject"
    repository_name = "TestRepo"
    folder_name = "src"
    file_name = "test_file.py"
    unique_id = uuid.uuid4().hex
    file_path = f"src/test_file_{unique_id}.py"
    content = "def test():\n    pass\n# This is a comment"
    lines = content.count('\n') + 1
    comments = 1
    tokens = 10
    hash_value = hashlib.sha256(content.encode('utf-8')).hexdigest()

    # Удаляем существующую запись, если она есть
    delete_file_record(file_path, hash_value)

    # Добавляем новую запись
    add_file_record(
        project_name=project_name,
        repository_name=repository_name,
        folder_name=folder_name,
        file_name=file_name,
        file_path=file_path,
        content=content,
        lines=lines,
        comments=comments,
        tokens=tokens,
        hash_value=hash_value,
        processed=False
    )

    # Получаем ID новой записи
    conn = create_connection(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM analysis_results
        WHERE file_path = ? AND hash = ?
    """, (file_path, hash_value))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0], file_path
    else:
        return None, file_path
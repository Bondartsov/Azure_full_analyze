# tests/test_update_file_record.py

import sys
import os
import hashlib
import uuid  # Для генерации уникальных ID
from datetime import datetime
import pytest
from sqlite3 import Error  # Добавлено для определения Error

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.utils.database import (
    add_file_record,
    update_file_record,
    delete_file_record,
    create_connection,
    DB_PATH
)
from core.logging.logger import log, setup_logging

@pytest.fixture(scope="function")
def setup_test_record():
    """
    Fixture to set up a test file record in the database.
    It adds a unique test record and ensures it's cleaned up after the test.
    """
    setup_logging()
    
    project_name = "TestProject"
    repository_name = "TestRepo"
    folder_name = "src"
    file_name = "test_file.py"
    unique_id = uuid.uuid4().hex  # Генерируем уникальный идентификатор
    file_path = f"src/test_file_{unique_id}.py"  # Используем уникальный file_path
    content = "def test():\n    pass\n# This is a comment"
    lines = content.count('\n') + 1
    comments = 1
    tokens = 10  # Примерное количество токенов
    hash_value = hashlib.sha256(content.encode('utf-8')).hexdigest()

    # Удаляем существующую запись, если она есть
    delete_success = delete_file_record(file_path, hash_value)
    if delete_success:
        log(f"🗑️ Существующая запись для {file_path} удалена.")
        print(f"🗑️ Существующая запись для {file_path} удалена.")

    # Добавляем запись
    success = add_file_record(
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
    assert success, "❌ Не удалось добавить тестовую запись."

    # Получаем ID записи
    conn = create_connection(DB_PATH)
    assert conn is not None, "❌ Не удалось подключиться к базе данных для получения ID записи."

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM analysis_results
            WHERE file_path = ? AND hash = ?
        """, (file_path, hash_value))
        result = cursor.fetchone()
    finally:
        conn.close()

    assert result is not None, "❌ Не удалось найти тестовую запись для обновления."
    file_id = result[0]
    assert isinstance(file_id, int), "❌ ID записи не является целым числом."
        
    yield file_id, file_path  # Provide the fixture value to the test

    # Teardown: удалить тестовую запись после теста
    teardown_success = delete_file_record(file_path, hash_value)
    if teardown_success:
        log(f"🗑️ Тестовая запись для {file_path} удалена после теста.")
        print(f"🗑️ Тестовая запись для {file_path} удалена после теста.")

def test_update_file_record(setup_test_record):
    """
    Тестирует обновление записи файла в базе данных.
    """
    file_id, file_path = setup_test_record
    assert file_id is not None, "❌ Не удалось найти тестовую запись для обновления."
    analysis = "Тестовый анализ ИИ."
    success = update_file_record(file_id, analysis)
    assert success, "❌ Не удалось обновить тестовую запись."

    # Проверяем обновлённую запись
    conn = create_connection(DB_PATH)
    assert conn is not None, "❌ Не удалось подключиться к базе данных для проверки обновления записи."

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT processed, analysis, date_updated FROM analysis_results
            WHERE id = ?
        """, (file_id,))
        record = cursor.fetchone()
    finally:
        conn.close()

    assert record is not None, "❌ Не удалось найти обновлённую запись для проверки."
    processed, analysis_result, date_updated = record

    assert processed == 1, "❌ Поле `processed` не было обновлено на `1`."
    assert analysis_result == "Тестовый анализ ИИ.", "❌ Поле `analysis` не содержит ожидаемый результат."
    assert date_updated is not None, "❌ Поле `date_updated` не установлено."

    log("✅ Тестовая запись успешно обновлена.")
    print("✅ Тестовая запись успешно обновлена.")

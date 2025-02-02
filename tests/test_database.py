# tests/test_database.py

import sys
import os

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.utils.database import add_file_record, create_connection, DB_PATH, update_file_record
from core.logging.logger import log, setup_logging

def create_test_file_record():
    project_name = "TestProject"
    repository_name = "TestRepo"
    folder_name = "src"
    file_name = "test_file.py"
    file_path = "src/test_file.py"
    content = "def test():\n    pass\n# This is a comment"
    lines = content.count('\n') + 1
    comments = 1
    tokens = 10  # Примерное количество токенов
    hash_value = "dummyhash123"

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

    # Проверяем, что запись успешно добавлена
    assert success, "❌ Не удалось добавить тестовую запись."
    log("✅ Тестовая запись успешно добавлена.")
    print("✅ Тестовая запись успешно добавлена.")

    # Получаем ID записи
    conn = create_connection(DB_PATH)
    assert conn is not None, "❌ Не удалось подключиться к базе данных для получения ID записи."
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM analysis_results
        WHERE file_path = ? AND hash = ?
    """, (file_path, hash_value))
    result = cursor.fetchone()
    conn.close()

    assert result is not None, "❌ Не удалось найти тестовую запись для обновления."
    file_id = result[0]
    return file_id

def test_add_file_record():
    file_id = create_test_file_record()
    # Проверяем, что ID тестовой записи получен
    assert file_id is not None, "ID тестовой записи не получен."

def test_update_file_record():
    setup_logging()
    file_id = create_test_file_record()
    analysis = "Тестовый анализ ИИ."
    success = update_file_record(file_id, analysis)
    if success:
        log("✅ Тестовая запись успешно обновлена.")
        print("✅ Тестовая запись успешно обновлена.")
    else:
        log("❌ Не удалось обновить тестовую запись.", level="ERROR")
        print("❌ Не удалось обновить тестовую запись.")
    assert success, "Не удалось обновить тестовую запись."

if __name__ == "__main__":
    test_update_file_record()

# core/utils/database.py

import sqlite3
from sqlite3 import Error
from core.logging.logger import log
import os
from datetime import datetime, timezone
import time

# Получаем путь к базе данных из переменной окружения или используем дефолтный путь
DB_PATH = os.getenv("FILES_DB_PATH", os.path.join(os.path.dirname(__file__), "../../files.db"))

def create_connection(db_file):
    """Создаёт соединение с SQLite базой данных и настраивает WAL режим."""
    conn = None
    try:
        conn = sqlite3.connect(db_file, timeout=30)  # Увеличиваем тайм-аут до 30 секунд
        log(f"✅ Подключение к базе данных {db_file} успешно установлено.")
        # Включаем WAL режим
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.close()
    except Error as e:
        log(f"❌ Ошибка подключения к базе данных {db_file}: {e}", level="ERROR")
    return conn

def create_table():
    """Создаёт таблицу analysis_results, если её нет."""
    conn = create_connection(DB_PATH)
    if conn is None:
        log("❌ Не удалось установить соединение с базой данных для создания таблицы.", level="ERROR")
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT,
                repository_name TEXT,
                folder_name TEXT,
                file_name TEXT,
                file_path TEXT UNIQUE,
                content TEXT,
                lines INTEGER,
                comments INTEGER,
                tokens INTEGER,
                hash TEXT,
                processed BOOLEAN,
                analysis TEXT,
                date_created TEXT,
                date_updated TEXT
            );
        """)
        conn.commit()
        log("✅ Таблица analysis_results успешно создана или уже существует.")
        return True
    except Error as e:
        log(f"❌ Ошибка при создании таблицы analysis_results: {e}", level="ERROR")
        return False
    finally:
        conn.close()


def add_file_record(project_name, repository_name, folder_name, file_name, file_path, content, lines, comments, tokens, hash_value, processed=False):
    """
    Добавляет запись о файле в таблицу analysis_results с ретраи при блокировке базы данных.

    :param project_name: Название проекта.
    :param repository_name: Название репозитория.
    :param folder_name: Название папки.
    :param file_name: Название файла.
    :param file_path: Полный путь к файлу.
    :param content: Содержимое файла.
    :param lines: Количество строк кода.
    :param comments: Количество комментариев.
    :param tokens: Количество токенов.
    :param hash_value: Хеш-сумма содержимого файла.
    :param processed: Флаг обработки (по умолчанию False).
    :return: True, если запись добавлена или обновлена успешно, иначе False.
    """
    max_retries = 5
    retry_delay = 0.5  # Начальная задержка в секундах

    for attempt in range(1, max_retries + 1):
        conn = create_connection(DB_PATH)
        if conn is None:
            log("❌ Не удалось установить соединение с базой данных.", level="ERROR")
            return False

        try:
            cursor = conn.cursor()
            # Проверяем, существует ли запись с тем же file_path и hash_value
            cursor.execute("""
                SELECT id, processed FROM analysis_results 
                WHERE file_path = ? AND hash = ?
            """, (file_path, hash_value))
            result = cursor.fetchone()

            if result:
                # Запись существует
                log(f"🔍 Запись для файла {file_path} уже существует.")
                file_id, is_processed = result
                if is_processed:
                    log(f"✅ Файл {file_path} уже был проанализирован ранее. Пропуск добавления.")
                    return True  # Файл уже обработан, пропускаем
                else:
                    # Обновляем существующую запись
                    current_time = datetime.now(timezone.utc).isoformat()
                    cursor.execute("""
                        UPDATE analysis_results
                        SET content = ?, lines = ?, comments = ?, tokens = ?, hash = ?, date_updated = ?
                        WHERE id = ?
                    """, (content, lines, comments, tokens, hash_value, current_time, file_id))
                    conn.commit()
                    log(f"🔄 Запись для файла {file_path} обновлена.")
                    return True
            else:
                # Добавляем новую запись с датой создания
                current_time = datetime.now(timezone.utc).isoformat()
                cursor.execute("""
                    INSERT INTO analysis_results (
                        project_name, repository_name, folder_name, file_name, file_path, content, lines, comments, tokens, hash, processed, date_created, date_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (project_name, repository_name, folder_name, file_name, file_path, content, lines, comments, tokens, hash_value, processed, current_time, current_time))
                conn.commit()
                log(f"➕ Запись для файла {file_path} добавлена.")
                return True

        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e).lower():
                log(f"⚠ Попытка {attempt}/{max_retries}: База данных заблокирована. Повторная попытка через {retry_delay} сек.")
                time.sleep(retry_delay)
                retry_delay *= 2  # Увеличиваем задержку для следующей попытки
                continue  # Переход к следующей итерации цикла
            else:
                log(f"❌ Операционная ошибка при добавлении/обновлении записи для файла {file_path}: {e}", level="ERROR")
                return False
        except Error as e:
            log(f"❌ Ошибка при добавлении/обновлении записи для файла {file_path}: {e}", level="ERROR")
            return False
        finally:
            conn.close()

    log(f"❌ Не удалось добавить/обновить файл {file_path} в базе данных после {max_retries} попыток.", level="ERROR")
    return False

def get_unprocessed_files():
    """
    Возвращает список файлов, которые ещё не были проанализированы ИИ.
    
    :return: Список записей о файлах.
    """
    conn = create_connection(DB_PATH)
    if conn is None:
        log("❌ Не удалось установить соединение с базой данных для выборки файлов.", level="ERROR")
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, project_name, repository_name, folder_name, file_name, file_path, content, lines, comments, tokens, hash
            FROM analysis_results
            WHERE processed = FALSE
        """)
        rows = cursor.fetchall()
        files = []
        for row in rows:
            files.append({
                "id": row[0],
                "project_name": row[1],
                "repository_name": row[2],
                "folder_name": row[3],
                "file_name": row[4],
                "file_path": row[5],
                "content": row[6],
                "lines": row[7],
                "comments": row[8],
                "tokens": row[9],
                "hash": row[10]
            })
        log(f"🔎 Найдено {len(files)} неанализированных файлов.")
        return files
    except Error as e:
        log(f"❌ Ошибка при выборке неанализированных файлов: {e}", level="ERROR")
        return []
    finally:
        conn.close()

def update_file_record(file_id, analysis):
    """
    Обновляет запись о файле после анализа ИИ.
    
    :param file_id: Идентификатор записи в базе данных.
    :param analysis: Результат анализа ИИ.
    :return: True, если обновление прошло успешно, иначе False.
    """
    max_retries = 5
    retry_delay = 0.5  # Начальная задержка в секундах

    for attempt in range(1, max_retries + 1):
        conn = create_connection(DB_PATH)
        if conn is None:
            log("❌ Не удалось установить соединение с базой данных для обновления записи.", level="ERROR")
            return False

        try:
            cursor = conn.cursor()
            current_time = datetime.now(timezone.utc).isoformat()
            log(f"🔄 Обновление записи {file_id} с анализом: {analysis}")
            cursor.execute("""
                UPDATE analysis_results
                SET processed = TRUE, analysis = ?, date_updated = ?
                WHERE id = ?
            """, (analysis, current_time, file_id))
            conn.commit()
            changes = cursor.rowcount
            log(f"📈 Изменённых строк: {changes}")
            if changes == 0:
                log(f"⚠️ Запись с id {file_id} не найдена для обновления.", level="WARNING")
            else:
                log(f"✅ Запись {file_id} обновлена: processed=True, analysis set.")
            return changes > 0

        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e).lower():
                log(f"⚠ Попытка {attempt}/{max_retries}: База данных заблокирована. Повторная попытка через {retry_delay} сек.")
                time.sleep(retry_delay)
                retry_delay *= 2  # Увеличиваем задержку для следующей попытки
                continue  # Переход к следующей итерации цикла
            else:
                log(f"❌ Операционная ошибка при обновлении записи {file_id}: {e}", level="ERROR")
                return False
        except Error as e:
            log(f"❌ Ошибка при обновлении записи {file_id}: {e}", level="ERROR")
            return False
        finally:
            conn.close()

    log(f"❌ Не удалось обновить запись {file_id} в базе данных после {max_retries} попыток.", level="ERROR")
    return False

def delete_file_record(file_path, hash_value):
    """
    Удаляет запись о файле из таблицы analysis_results.
    
    :param file_path: Полный путь к файлу.
    :param hash_value: Хеш-сумма содержимого файла.
    :return: True, если запись удалена успешно, иначе False.
    """
    conn = create_connection(DB_PATH)
    if conn is None:
        log("❌ Не удалось установить соединение с базой данных для удаления записи.", level="ERROR")
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM analysis_results
            WHERE file_path = ? AND hash = ?
        """, (file_path, hash_value))
        conn.commit()
        if cursor.rowcount > 0:
            log(f"🗑️ Запись для файла {file_path} удалена.")
            return True
        else:
            log(f"⚠️ Запись для файла {file_path} не найдена для удаления.", level="WARNING")
            return False
    except Error as e:
        log(f"❌ Ошибка при удалении записи для файла {file_path}: {e}", level="ERROR")
        return False
    finally:
        conn.close()
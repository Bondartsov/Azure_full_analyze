# core/utils/token_counter.py
# анализирует файлы

import os
from tqdm import tqdm
from core.azure.repos import get_repo_files
from dotenv import load_dotenv  # Для загрузки переменных из .env
import tiktoken
from core.logging.logger import log  # Убедитесь, что логгер импортирован
from core.utils.database import add_file_record  # Импортируем функцию из database.py
from core.azure.connection import connect_to_azure  # Предполагаемый импорт для подключения к Azure
import hashlib  # Для вычисления хеша

# Загрузка переменных окружения из .env
load_dotenv()

# Получение белого списка из переменной окружения
WHITE_EXTENSIONS = set(ext.strip().lower() for ext in os.getenv("WHITE_EXTENSIONS", "").split(",") if ext.strip())
if not WHITE_EXTENSIONS:
    log("⚠ Переменная WHITE_EXTENSIONS пуста! Будут анализироваться все файлы.", level="WARNING")
    print("⚠ Переменная WHITE_EXTENSIONS пуста! Будут анализироваться все файлы.")
else:
    log(f"📂 Белый список расширений: {WHITE_EXTENSIONS}")
    print(f"📂 Белый список расширений: {WHITE_EXTENSIONS}")

def get_file_content(project_name, repository_name, file_path):
    """
    Загружает содержимое файла по его пути через API Azure DevOps.
    """
    try:
        connection = connect_to_azure()
        git_client = connection.clients.get_git_client()

        log(f"📄 Загрузка файла {file_path} из репозитория {repository_name}...")
        content_generator = git_client.get_item_content(repository_name, path=file_path, project=project_name)

        # Корректно извлекаем данные из генератора
        file_content = b"".join(content_generator).decode("utf-8", errors="ignore")

        if file_content:
            log(f"✅ Файл {file_path} успешно загружен ({len(file_content)} символов)")
            print(f"✅ Файл {file_path} успешно загружен ({len(file_content)} символов)")
        else:
            log(f"⚠ Файл {file_path} пуст или не удалось загрузить", level="WARNING")
            print(f"⚠ Файл {file_path} пуст или не удалось загрузить")

        return file_content if file_content else ""
    except Exception as e:
        log(f"❌ Ошибка при загрузке файла {file_path}: {e}", level="ERROR")
        print(f"❌ Ошибка при загрузке файла {file_path}: {e}")
        return ""

def count_tokens_in_repo(project_name, repository_name):
    """
    Считает токены, строки кода и комментарии в файлах (у которых расширения в WHITE_EXTENSIONS).
    Возвращает (files_data, total_tokens).
    files_data -> [{"path": ..., "tokens": int, "lines": int, "comments": int}, ...]
    """
    total_tokens = 0
    files_data = []
    log(f"📊 Начало подсчёта токенов, строк и комментариев в {repository_name} (белый список).")

    files = get_repo_files(project_name, repository_name)
    if not files:
        log(f"⚠ Не удалось получить файлы для {repository_name}", level="WARNING")
        return [], 0

    for file_path in tqdm(files, desc="Обработка файлов"):
        _, ext = os.path.splitext(file_path.lower())
        if ext not in WHITE_EXTENSIONS:
            log(f"🔍 Файл {file_path} пропущен: расширение {ext} не в белом списке.")
            continue

        content = get_file_content(project_name, repository_name, file_path)

        if not content.strip():
            log(f"🔍 Файл {file_path} пропущен: пустое содержимое.")
            continue

        log(f"📝 Содержимое файла {file_path}: {len(content)} символов")
        print(f"📝 Содержимое файла {file_path}: {len(content)} символов")

        # Подсчитываем токены
        tokens_count = count_tokens_in_text(content)

        # Подсчитываем строки (простой способ)
        lines_count = content.count('\n') + 1

        # Подсчитываем комментарии (наивная реализация)
        comments_count = count_comments_naive(content, ext)

        # Вычисляем хеш-сумму содержимого файла
        hash_value = hashlib.sha256(content.encode('utf-8')).hexdigest()

        # Добавляем запись в базу данных
        success = add_file_record(
            project_name=project_name,
            repository_name=repository_name,
            folder_name=os.path.dirname(file_path),
            file_name=os.path.basename(file_path),
            file_path=file_path,
            content=content,
            lines=lines_count,
            comments=comments_count,
            tokens=tokens_count,
            hash_value=hash_value,
            processed=False  # Флаг обработки устанавливается как False
        )

        if success:
            log(f"✅ Файл {file_path} успешно добавлен/обновлён в базе данных.")
        else:
            log(f"❌ Не удалось добавить/обновить файл {file_path} в базе данных.", level="ERROR")

        # Добавляем данные в files_data для дальнейшего анализа (если нужно)
        files_data.append({
            "path": file_path,
            "tokens": tokens_count,
            "lines": lines_count,
            "comments": comments_count,
        })
        total_tokens += tokens_count

    log(f"📈 Общее количество токенов в репозитории {repository_name}: {total_tokens}")
    return files_data, total_tokens

def read_file_content(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            log(f"📂 Файл {file_path} успешно прочитан, {len(content)} символов.")
            return content
    except Exception as e:
        log(f"❌ Ошибка при чтении файла {file_path}: {e}", level="ERROR")
        return ""

def count_tokens_in_text(text, model="cl100k_base"):
    """
    Подсчитывает количество токенов в тексте с использованием tiktoken.
    Всегда использует явную кодировку 'cl100k_base'.
    """
    try:
        # Используем явную кодировку 'cl100k_base'
        encoding = tiktoken.get_encoding("cl100k_base")
    except Exception as e:
        log(f"❌ Ошибка при получении кодировки 'cl100k_base': {e}", level="ERROR")
        raise e

    tokens = encoding.encode(text)
    token_count = len(tokens)
    log(f"🪄 Подсчитано {token_count} токенов.")
    print(f"🪄 Подсчитано {token_count} токенов.")
    return token_count

def split_text(text, max_tokens=3000):
    """
    Разделяет текст на части, каждая из которой не превышает max_tokens.
    Всегда использует явную кодировку 'cl100k_base'.
    """
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
    except Exception as e:
        log(f"❌ Ошибка при получении кодировки 'cl100k_base': {e}", level="ERROR")
        raise e

    tokens = encoding.encode(text)
    parts = []
    current_tokens = []

    for token in tokens:
        current_tokens.append(token)
        if len(current_tokens) >= max_tokens:
            decoded_part = encoding.decode(current_tokens)
            parts.append(decoded_part)
            log(f"📚 Разделено на {len(decoded_part)} символов.")
            print(f"📚 Разделено на {len(decoded_part)} символов.")
            current_tokens = []

    if current_tokens:
        decoded_part = encoding.decode(current_tokens)
        parts.append(decoded_part)
        log(f"📚 Разделено на {len(decoded_part)} символов.")
        print(f"📚 Разделено на {len(decoded_part)} символов.")

    log(f"📑 Общее количество частей после разбиения: {len(parts)}")
    print(f"📑 Общее количество частей после разбиения: {len(parts)}")
    return parts

def count_comments_naive(content, ext):
    """
    Наивно считает комментарии для ряда языков:
    - C-like (C#, C++, Java, JS): ищем строки //, /*...*/
    - Python: строки, начинающиеся с #
    и т.д.
    """
    lines = content.split('\n')
    comment_lines = 0
    in_block_comment = False

    for line in lines:
        stripped = line.strip()

        # Проверяем Python-style #
        if ext == '.py':
            if stripped.startswith('#'):
                comment_lines += 1
                continue

        # C++/Java/C#/JS single line //
        if stripped.startswith('//') and ext in ['.cpp', '.c', '.cs', '.java', '.js', '.ts', '.jsx', '.tsx']:
            comment_lines += 1
            continue

        # Начало блокового комментария /* */
        if '/*' in stripped and ext in ['.cpp', '.c', '.cs', '.java', '.js', '.ts', '.jsx', '.tsx']:
            in_block_comment = True
            comment_lines += 1
            # Если блоковый комментарий закрывается в той же строке
            if '*/' in stripped and stripped.index('/*') < stripped.index('*/'):
                in_block_comment = False
            continue

        # Внутри блокового комментария
        if in_block_comment:
            comment_lines += 1
            if '*/' in stripped:
                in_block_comment = False
            continue

    log(f"📝 Найдено {comment_lines} строк комментариев для расширения {ext}.")
    print(f"📝 Найдено {comment_lines} строк комментариев для расширения {ext}.")
    return comment_lines
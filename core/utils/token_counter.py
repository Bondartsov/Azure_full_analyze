import tiktoken
from tqdm import tqdm
import os
from core.azure.repos import get_repo_files, get_file_content
from core.logging.logger import log
from dotenv import load_dotenv  # Для загрузки переменных из .env

# Загрузка переменных окружения из .env
load_dotenv()

# Получение белого списка из переменной окружения
WHITE_EXTENSIONS = set(os.getenv("WHITE_EXTENSIONS", "").split(","))

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
            continue

        content = get_file_content(project_name, repository_name, file_path)
        if not content.strip():
            continue

        # Подсчитываем токены
        tokens_count = count_tokens_in_text(content)

        # Подсчитываем строки (простой способ)
        lines_count = content.count('\n') + 1

        # Подсчитываем комментарии (наивная реализация)
        comments_count = count_comments_naive(content, ext)

        files_data.append({
            "path": file_path,
            "tokens": tokens_count,
            "lines": lines_count,
            "comments": comments_count,
        })
        total_tokens += tokens_count

    return files_data, total_tokens

def count_tokens_in_text(text, model_encoding="cl100k_base"):
    encoding = tiktoken.get_encoding(model_encoding)
    return len(encoding.encode(text))

def count_comments_naive(content, ext):
    """
    Наивно считает комментарии для ряда языков:
    - C-like (C#, C++, Java, JS): ищем строки //, /*...*/
    - Python: строки, начинающиеся с #
    и т.д.
    """
    # Разбиваем на строки
    lines = content.split('\n')
    comment_lines = 0
    in_block_comment = False  # для /* ... */
    
    for line in lines:
        stripped = line.strip()

        # Проверяем Python-style #
        # Например, если ext == '.py', то можно считать # как комментарий
        if ext == '.py':
            if stripped.startswith('#'):
                comment_lines += 1
                continue

        # C++/Java/C#/JS single line //
        if stripped.startswith('//'):
            comment_lines += 1
            continue

        # Блоковые /* ... */
        if '/*' in stripped:
            in_block_comment = True
            comment_lines += 1  # считаем, что вся строка - комментарий
            if '*/' in stripped and stripped.index('/*') < stripped.index('*/'):
                # Если в одной строке открывается и закрывается
                in_block_comment = False
            continue
        if in_block_comment:
            comment_lines += 1
            # проверяем, не закрывается ли
            if '*/' in stripped:
                in_block_comment = False
            continue

    return comment_lines

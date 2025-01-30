import tiktoken
from tqdm import tqdm
import os

from core.azure.repos import get_repo_files, get_file_content
from core.logging.logger import log

WHITE_EXTENSIONS = {
    # Back-end
    ".py", ".java", ".cs", ".c", ".h", ".cpp", ".hpp", ".go", ".php", ".rb", ".rs", ".kt", ".scala",
    # Node.js (server)
    ".js", ".mjs", ".cjs", ".ts",
    # Frontend (Web)
    ".html", ".css", ".scss", ".sass", ".jsx", ".tsx", ".vue", ".svelte",
    # iOS
    ".swift",  # Swift
    ".m",      # Objective-C
    ".mm",     # Objective-C++
    # Android (Java/Kotlin уже выше)
    # Кроссплатформенные
    ".dart",   # Flutter
}

def count_tokens_in_repo(project_name, repository_name):
    """
    Подсчитывает количество токенов ТОЛЬКО в файлах, чьи расширения содержатся в WHITE_EXTENSIONS.

    Возвращает кортеж: (files_data, total_tokens), где
        files_data = [
            {"path": <строка>, "tokens": <число>},
            ...
        ]
        total_tokens (int)
    """
    total_tokens = 0
    files_data = []
    excluded_files = 0

    log(f"📊 Начало подсчёта токенов в репозитории {repository_name} (белый список)...")

    files = get_repo_files(project_name, repository_name)
    if not files:
        log(f"⚠ Не удалось получить файлы для {repository_name}.", level="WARNING")
        return [], 0

    for file_path in tqdm(files, desc="Обработка файлов"):
        # Определяем расширение
        _, ext = os.path.splitext(file_path.lower())

        if ext not in WHITE_EXTENSIONS:
            excluded_files += 1
            continue

        content = get_file_content(project_name, repository_name, file_path)
        if not content.strip():
            log(f"⚠ Файл {file_path} пуст или не удалось прочитать содержимое.")
            continue

        tokens_count = count_tokens_in_text(content)
        files_data.append({
            "path": file_path,
            "tokens": tokens_count
        })
        total_tokens += tokens_count

        log(f"📄 Файл {file_path} → {tokens_count} токенов")

    log(f"✅ DEBUG: В репозитории {repository_name} "
        f"обработано {len(files_data)} файлов (по белому списку), "
        f"пропущено {excluded_files}, всего токенов: {total_tokens}")

    return files_data, total_tokens

def count_tokens_in_text(text, model_encoding="cl100k_base"):
    """Подсчитывает количество токенов в тексте, используя указанную модель кодировки (по умолчанию cl100k_base)."""
    encoding = tiktoken.get_encoding(model_encoding)
    return len(encoding.encode(text))

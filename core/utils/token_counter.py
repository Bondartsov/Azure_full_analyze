import tiktoken
from core.azure.repos import get_repo_files, get_file_content
from core.logging.logger import log
from tqdm import tqdm

# Исключаемые расширения файлов
EXCLUDE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".bmp", ".tiff", ".ico",  # Изображения
    ".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm",  # Видео
    ".mp3", ".wav", ".ogg", ".flac", ".aac", ".wma",  # Аудио
    ".ttf", ".otf", ".woff", ".woff2",  # Шрифты
    ".bin", ".dylib", ".so", ".o", ".dll",  # Бинарные файлы
    ".zip", ".tar", ".gz", ".bz2", ".7z",  # Архивы
    ".ckpt", ".pb", ".pt", ".onnx",  # Модели нейросетей
    ".sqlite", ".db", ".sql", ".mdb", ".accdb"  # Файлы баз данных
}

def count_tokens_in_repo(project_name, repository_name):
    """Подсчитывает количество токенов в репозитории, исключая бинарные файлы."""
    total_tokens = 0
    token_data = {}
    excluded_files = 0

    log(f"📊 Начало подсчёта токенов в репозитории {repository_name}...")
    
    # Получение списка файлов в репозитории
    files = get_repo_files(project_name, repository_name)
    if not files:
        log(f"⚠ Не удалось получить файлы для {repository_name}.", level="WARNING")
        return {}, 0

    for file_path in tqdm(files, desc="Обработка файлов"):
        # Проверяем расширение файла
        if any(file_path.lower().endswith(ext) for ext in EXCLUDE_EXTENSIONS):
            log(f"⚠ Файл {file_path} исключён (неподдерживаемый формат)")
            excluded_files += 1
            continue

        # Загружаем содержимое файла
        content = get_file_content(project_name, repository_name, file_path)
        if not content.strip():
            log(f"⚠ Файл {file_path} пуст или не удалось прочитать")
            continue

        # Подсчёт токенов
        tokens = count_tokens_in_text(content)
        token_data[file_path] = tokens
        total_tokens += tokens
        log(f"📄 Файл {file_path} → {tokens} токенов")

    log(f"✅ DEBUG: В репозитории **{repository_name}** обработано **{len(token_data)} файла(ов)**, общее количество токенов: **{total_tokens}**")
    
    return token_data, total_tokens

def count_tokens_in_text(text, model_encoding="cl100k_base"):
    """Подсчитывает количество токенов в тексте."""
    encoding = tiktoken.get_encoding(model_encoding)
    return len(encoding.encode(text))

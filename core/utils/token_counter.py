import tiktoken
from tqdm import tqdm
import os

from core.azure.repos import get_repo_files, get_file_content
from core.logging.logger import log

WHITE_EXTENSIONS = {
    # Back-end (Бэкенд)
    ".py",  # Python
    ".java",  # Java
    ".cs",  # C#
    ".c",  # C
    ".h",  # C Header Files
    ".cpp",  # C++
    ".hpp",  # C++ Header Files
    ".php",  # PHP
    ".kt",  # Kotlin
    
    # Frontend (Фронтенд)
    ".html",  # HTML
    ".css",  # CSS
    ".scss",  # SASS/SCSS
    ".sass",  # SASS
    ".jsx",  # React JSX
    ".tsx",  # TypeScript + JSX
    ".vue",  # Vue.js Single File Components
    ".svelte",  # Svelte Components
    ".ts",  # TypeScript (for Angular)
    
    # Styles (Стили)
    ".css",  # CSS
    ".scss",  # SASS/SCSS
    ".sass",  # SASS
    ".less",  # LESS
    
    # Scripts (Скрипты)
    ".js",  # JavaScript
    ".mjs",  # ES Module JavaScript
    ".cjs",  # CommonJS JavaScript
    
    # PLC (Программируемые логические контроллеры)
    ".CHK",  # PLC Program Check Files
    ".PRG",  # PLC Program Files
    ".pro",  # PLC Project Files
    ".SDB",  # PLC Database Files
    ".SYM",  # Symbol Files
    ".wibu.ini",  # Wibu-Systems License Configuration
    ".ci",  # Code Interface Files
    ".ECI",  # Extended Code Interface Files
    ".ri",  # Resource Interface Files

    # General Embedded System Files (Общие файлы встраиваемых систем)
    ".library",  # Library Files
    ".export",  # Exported Files
    ".ecp",  # Embedded Control Project Files
    ".project",  # Project Files
    
    # Mobile Development (Мобильная Разработка)
    ".swift",  # Swift for iOS
    ".m",  # Objective-C for iOS
    ".mm",  # Objective-C++ for iOS
    ".kt",  # Kotlin for Android (already included in backend section)
    ".java",  # Java for Android (already included in backend section)
    ".dart",  # Flutter for Cross-Platform Mobile Development
    
    # Test Files (Тестовые файлы)
    ".test.js", ".spec.js",  # JavaScript Tests
    ".test.ts", ".spec.ts",  # TypeScript Tests
    ".java",  # Java Tests (JUnit)
    ".py",  # Python Tests (unittest, pytest)
    ".kt",  # Kotlin Tests
    
    # Configuration Files (Конфигурационные файлы)
    ".csproj",  # C# Project File
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

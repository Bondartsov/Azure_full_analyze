import json
import os
from core.logging.logger import log

CACHE_DIR = "cache"

def get_cache_path(project_name, repository_name=None):
    """
    Возвращает путь к файлу кэша.
    Если repository_name не указано, считается, что мы хотим сохранить сводный кэш по всему проекту.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    if repository_name:
        return os.path.join(CACHE_DIR, f"{project_name}_{repository_name}.json")
    return os.path.join(CACHE_DIR, f"{project_name}_summary.json")

def load_cache(project_name, repository_name=None):
    """Загружает данные из кэша (json)."""
    cache_file = get_cache_path(project_name, repository_name)
    if not os.path.exists(cache_file):
        return None
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"⚠ Ошибка загрузки кэша {cache_file}: {e}", level="ERROR")
        return None

def save_cache(data, project_name, repository_name=None):
    """Сохраняет данные в кэш (json)."""
    cache_file = get_cache_path(project_name, repository_name)
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        log(f"✅ Кэш сохранён: {cache_file}")
    except Exception as e:
        log(f"⚠ Ошибка сохранения кэша {cache_file}: {e}", level="ERROR")

def is_repo_changed(project_name, repository_name, latest_commit=None):
    """
    Проверяем, изменился ли репозиторий, глядя только на файлы.
    Параметр latest_commit добавлен для совместимости, но здесь не используется.
    Если в кэше есть список файлов и у каждого есть "hash",
    мы сверяем его с текущим хешем.
    Если хотя бы один файл не совпал — считаем, что репозиторий изменился.

    Если кэша нет — считаем, что репо новое или изменилось.
    """
    cached_data = load_cache(project_name, repository_name)
    if not cached_data:
        return True  # Нет кэша → новое/изменённое

    cached_files = cached_data.get("files", [])
    for file_info in cached_files:
        if "path" not in file_info or "hash" not in file_info:
            return True  # Данных недостаточно, нужно пересчитать

        current_hash = get_file_hash(file_info["path"])
        if file_info["hash"] != current_hash:
            return True  # Файл изменился

    return False

def save_repo_data_to_cache(project_name, repository_name, total_tokens, files_data):
    """
    Сохраняет данные о репозитории в кэш.
    :param project_name: Название проекта
    :param repository_name: Название репозитория
    :param total_tokens: Общее число токенов
    :param files_data: Список словарей вида [{"path": "...", "tokens": N}, ...]
                       Желательно при сохранении заполнить "hash" у каждого файла,
                       чтобы потом корректно определять изменения.
    """
    data = {
        "total_tokens": total_tokens,
        "files": files_data
    }
    # Дополняем "hash" для каждого файла
    for f in data["files"]:
        if "path" in f:
            f["hash"] = get_file_hash(f["path"])

    save_cache(data, project_name, repository_name)

def load_repo_data_from_cache(project_name, repository_name):
    """
    Загружает данные репозитория из кэша.
    Возвращает dict, содержащий "total_tokens" и "files",
    или None, если кэша нет.
    """
    cached_data = load_cache(project_name, repository_name)
    if not cached_data:
        return None
    return cached_data

def get_file_hash(file_path):
    """
    Генерирует хеш файла для проверки изменений.
    NB: Эта функция не знает о project_name/repository_name,
        просто читает локальный файл.
    """
    from hashlib import sha256
    try:
        with open(file_path, "rb") as f:
            return sha256(f.read()).hexdigest()
    except Exception:
        return None  # Если файл отсутствует или ошибка чтения

def clear_cache_for_repo(project_name, repository_name):
    """Удаляет кэш для одного репозитория (файл {project_name}_{repository_name}.json)."""
    cache_file = get_cache_path(project_name, repository_name)
    if os.path.exists(cache_file):
        os.remove(cache_file)
        log(f"🗑️ Кэш удалён для репозитория: {repository_name}")

def clear_project_summary_cache(project_name):
    """
    Удаляет все файлы кэша для данного проекта (включая сводный).
    Т.е. любой файл, начинающийся с "{project_name}_" в папке cache.
    Пример: "ST.CPM_Infrastructure.json", "ST.CPM_summary.json", ...
    """
    if not os.path.exists(CACHE_DIR):
        return

    cache_files = os.listdir(CACHE_DIR)
    pattern = f"{project_name}_"
    removed_any = False

    for filename in cache_files:
        if filename.startswith(pattern):
            full_path = os.path.join(CACHE_DIR, filename)
            if os.path.isfile(full_path):
                os.remove(full_path)
                removed_any = True
                log(f"🗑️ Кэш {filename} удалён для проекта: {project_name}")

    if not removed_any:
        log(f"⚠ Не найдено файлов кэша для проекта: {project_name}")
    else:
        log(f"✅ Кэш проекта {project_name} успешно очищен!")

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
        # Нет кэша, значит новый или изменён
        return True

    cached_files = cached_data.get("files", [])
    for file_info in cached_files:
        if "path" not in file_info or "hash" not in file_info:
            # Если нет пути или хеша, считаем, что нужно пересчитать
            return True

        current_hash = get_file_hash(file_info["path"])
        if file_info["hash"] != current_hash:
            return True

    return False

def save_repo_data_to_cache(project_name, repository_name, total_tokens, files_data):
    """
    Сохраняет данные о репозитории в кэш.
    :param project_name: Название проекта
    :param repository_name: Название репозитория
    :param total_tokens: Общее число токенов
    :param files_data: Список словарей вида [{"path": "...", "tokens": N}, ...]
                       Желательно дополнить каждый объект "hash": хеш_файла,
                       чтобы потом корректно отрабатывать is_repo_changed.
    """
    data = {
        "total_tokens": total_tokens,
        "files": files_data
    }
    # Если хотим, можем тут же добавить поле "hash" для каждого файла
    # при сохранении, чтобы потом корректно проверять изменения:
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
        # Если файл отсутствует или ошибка чтения
        return None

def clear_cache_for_repo(project_name, repository_name):
    """Удаляет кэш для одного репозитория."""
    cache_file = get_cache_path(project_name, repository_name)
    if os.path.exists(cache_file):
        os.remove(cache_file)
        log(f"🗑️ Кэш удалён для репозитория: {repository_name}")

def clear_project_summary_cache(project_name):
    """Удаляет сводный кэш проекта."""
    cache_file = get_cache_path(project_name)
    if os.path.exists(cache_file):
        os.remove(cache_file)
        log(f"🗑️ Кэш удалён для проекта: {project_name}")

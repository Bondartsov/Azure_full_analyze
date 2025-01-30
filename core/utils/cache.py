import json
import os
from core.logging.logger import log

CACHE_DIR = "cache"

def get_cache_path(project_name, repository_name=None):
    """Возвращает путь к файлу кэша."""
    os.makedirs(CACHE_DIR, exist_ok=True)  # Гарантируем, что папка для кэша существует
    if repository_name:
        return os.path.join(CACHE_DIR, f"{project_name}_{repository_name}.json")
    return os.path.join(CACHE_DIR, f"{project_name}_summary.json")

def load_cache(project_name, repository_name=None):
    """Загружает данные кэша."""
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
    """Сохраняет данные в кэш."""
    cache_file = get_cache_path(project_name, repository_name)

    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        log(f"✅ Кэш сохранён: {cache_file}")
    except Exception as e:
        log(f"⚠ Ошибка сохранения кэша {cache_file}: {e}", level="ERROR")

def is_repo_changed(project_name, repository_name, latest_commit):
    """
    Проверяет, изменился ли репозиторий по последнему коммиту или файлам.
    ВАЖНО: Сейчас last_commit в кэше хранится commit_count, а не реальный хеш!
           Поэтому сравнение cached_data.get("last_commit") != latest_commit
           (где latest_commit - строка-хеш) всегда будет True.
    """
    cached_data = load_cache(project_name, repository_name)

    if not cached_data:
        return True  # Нет данных — значит, репозиторий новый

    # Сравнение "last_commit" и latest_commit не будет работать корректно,
    # так как в "last_commit" фактически лежит число коммитов (commit_count).
    if cached_data.get("last_commit") != latest_commit:
        return True

    # Проверяем изменения по файлам
    cached_files = cached_data.get("files", [])
    for file in cached_files:
        if "path" in file and "hash" in file:
            if file["hash"] != get_file_hash(project_name, repository_name, file["path"]):
                return True  # Файл изменился

    return False  # Изменений не найдено

def save_repo_data_to_cache(project_name, repository_name, total_tokens, commit_count, files_data, analysis):
    """
    Сохраняет данные о репозитории в кэш.

    :param project_name: Название проекта
    :param repository_name: Название репозитория
    :param total_tokens: Общее число токенов
    :param commit_count: Количество коммитов (на текущий момент используется вместо last_commit!)
    :param files_data: Список (или словарь) данных по файлам
    :param analysis: Результат анализа (dict)
    """
    # last_commit фактически записываем числом commit_count. 
    # Если хочешь хранить реальный хеш, передавай его сюда вместо commit_count.
    data = {
        "last_commit": commit_count,  # ВНИМАНИЕ: здесь commit_count вместо реального коммита
        "total_tokens": total_tokens,
        "commit_count": commit_count,
        "files": files_data,
        "analysis": analysis
    }
    save_cache(data, project_name, repository_name)

def load_repo_data_from_cache(project_name, repository_name):
    """
    Загружает данные репозитория из кэша.
    Возвращает кортеж:
    (total_tokens, commit_count, files_data, analysis) или None, если кэша нет.
    """
    cached_data = load_cache(project_name, repository_name)
    if not cached_data:
        return None

    total_tokens = cached_data.get("total_tokens", 0)
    commit_count = cached_data.get("commit_count", 0)
    files_data = cached_data.get("files", [])
    analysis = cached_data.get("analysis", {})

    return total_tokens, commit_count, files_data, analysis

def get_file_hash(project_name, repository_name, file_path):
    """Генерирует хеш файла для проверки изменений."""
    from hashlib import sha256
    try:
        with open(file_path, "rb") as f:
            return sha256(f.read()).hexdigest()
    except Exception:
        return None  # Если файл отсутствует или ошибка чтения, возвращаем None

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

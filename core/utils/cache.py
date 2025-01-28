import json
import os
from core.logging.logger import log

CACHE_FILE = "./cache.json"

def load_cache():
    """Загружает данные кэша из файла."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            log(f"Ошибка загрузки кэша: {e}", level="ERROR")
    return {}

def save_cache(cache):
    """Сохраняет данные в файл кэша."""
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=4)
    except Exception as e:
        log(f"Ошибка сохранения кэша: {e}", level="ERROR")

def is_repo_changed(project_name, repository_name, latest_commit):
    """
    Проверяет, изменился ли репозиторий, основываясь на хэше последнего коммита.
    """
    cache = load_cache()
    key = f"{project_name}/{repository_name}"
    if key in cache and cache[key] == latest_commit:
        log(f"Репозиторий {repository_name} не изменился, пропускаем.")
        return False
    # Обновляем кэш
    cache[key] = latest_commit
    save_cache(cache)
    return True

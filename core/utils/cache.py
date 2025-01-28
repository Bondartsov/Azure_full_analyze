import json
import os
from core.logging.logger import log

CACHE_FILE = "./cache.json"


def load_cache():
    """Загружает данные кэша из файла и корректирует его структуру."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)

            # Преобразование старого формата (если значение — строка, заменяем на словарь)
            for key, value in cache.items():
                if isinstance(value, str):
                    cache[key] = {"last_commit": value, "tokens": 0, "commits": 0}

            return cache

        except json.JSONDecodeError:
            log("⚠ Ошибка декодирования JSON кэша. Файл повреждён, создаю новый.", level="ERROR")
        except Exception as e:
            log(f"⚠ Ошибка загрузки кэша: {e}", level="ERROR")

    return {}  # Возвращаем пустой кэш, если файла нет или произошла ошибка


def save_cache(cache):
    """Сохраняет данные в файл кэша."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=4, ensure_ascii=False)
    except Exception as e:
        log(f"⚠ Ошибка сохранения кэша: {e}", level="ERROR")


def is_repo_changed(project_name, repository_name, latest_commit):
    """
    Проверяет, изменился ли репозиторий, основываясь на хэше последнего коммита.
    Если репозиторий НЕ изменился, загружает данные из кэша.
    """
    cache = load_cache()
    key = f"{project_name}/{repository_name}"

    if key in cache and cache[key].get("last_commit") == latest_commit:
        log(f"🔄 Репозиторий {repository_name} не изменился, загружаем данные из кэша.")
        return False  # Репозиторий не изменился

    # Обновляем кэш
    cache[key] = {"last_commit": latest_commit, "tokens": 0, "commits": 0}  # Сбрасываем токены и коммиты при изменении
    save_cache(cache)
    return True  # Репозиторий изменился


def save_repo_data_to_cache(project_name, repository_name, total_tokens, commit_count):
    """Сохраняет информацию о репозитории в кэш."""
    cache = load_cache()
    key = f"{project_name}/{repository_name}"

    if key not in cache:
        cache[key] = {}

    cache[key]["tokens"] = total_tokens
    cache[key]["commits"] = commit_count

    save_cache(cache)


def load_repo_data_from_cache(project_name, repository_name):
    """Загружает информацию о репозитории из кэша, если она есть."""
    cache = load_cache()
    key = f"{project_name}/{repository_name}"

    if key in cache:
        return cache[key].get("tokens", 0), cache[key].get("commits", 0)

    return None  # Если данных нет, возвращаем None


def load_all_project_data_from_cache(project_name):
    """
    Загружает все данные о репозиториях проекта из кэша.
    Используется для генерации саммари-отчёта.
    """
    cache = load_cache()
    project_data = {}

    for key, data in cache.items():
        if key.startswith(f"{project_name}/"):
            repo_name = key.split("/")[-1]
            project_data[repo_name] = {
                "tokens": data.get("tokens", 0),
                "commits": data.get("commits", 0)
            }

    return project_data

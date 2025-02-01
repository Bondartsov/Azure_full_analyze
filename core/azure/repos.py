import os
from core.azure.connection import connect_to_azure
from core.logging.logger import log
from azure.devops.v7_0.git.models import GitRepository
from tqdm import tqdm  # Прогресс-бар для операций с файлами

def get_repositories(project_name):
    """
    Получает список репозиториев в указанном проекте и возвращает объекты с полями .id и .name.
    """
    try:
        connection = connect_to_azure()
        git_client = connection.clients.get_git_client()
        
        log(f"📌 Запрос списка репозиториев для проекта {project_name}...")
        repos = git_client.get_repositories(project=project_name)

        if not repos:
            log(f"⚠ Нет репозиториев в проекте {project_name}.", level="WARNING")
            return []

        repo_list = [repo for repo in repos if isinstance(repo, GitRepository)]
        log(f"✅ Получено {len(repo_list)} репозиториев: {[repo.name for repo in repo_list]}")
        return repo_list  # Возвращаем список объектов, а не просто имена

    except Exception as e:
        log(f"❌ Ошибка при получении репозиториев: {str(e)}", level="ERROR")
        return []


def fetch_files_from_azure(project_name, repository_name):
    """
    Получает список файлов в репозитории через API Azure DevOps.
    """
    try:
        connection = connect_to_azure()
        git_client = connection.clients.get_git_client()

        log(f"📂 Запрос списка файлов для репозитория {repository_name}...")
        items = git_client.get_items(project=project_name, repository_id=repository_name, recursion_level="full")

        if not items:
            log(f"⚠ Репозиторий {repository_name} не содержит файлов или доступ ограничен.", level="WARNING")
            return []

        # Фильтруем только пути файлов
        file_paths = [item.path for item in items if not item.is_folder]
        log(f"✅ Получено {len(file_paths)} файлов из {repository_name}")
        return file_paths

    except Exception as e:
        log(f"❌ Ошибка при получении файлов из {repository_name}: {e}", level="ERROR")
        return []


def get_repo_files(project_name, repository_name):
    """
    Получает список файлов в репозитории, используя `fetch_files_from_azure`.
    """
    try:
        files = fetch_files_from_azure(project_name, repository_name)

        if not files:
            log(f"⚠ DEBUG: В репозитории **{repository_name}** **не найдено файлов**. Возможные причины:\n"
                f"   - 🔹 Репозиторий пуст\n"
                f"   - 🔹 Ошибка при получении файлов\n"
                f"   - 🔹 Недостаточно прав доступа\n"
                f"   - 🔹 Сбой сети/API", level="WARNING")
            return None

        return files

    except Exception as e:
        log(f"❌ Ошибка при получении файлов из {repository_name}: {e}", level="ERROR")
        return None


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
        else:
            log(f"⚠ Файл {file_path} пуст или не удалось загрузить", level="WARNING")

        return file_content if file_content else ""

    except Exception as e:
        log(f"❌ Ошибка при загрузке файла {file_path}: {e}", level="ERROR")
        return ""

import os
from core.azure.connection import connect_to_azure
from core.logging.logger import log
from azure.devops.v7_0.git.models import GitRepository
from tqdm import tqdm  # Добавляем прогресс-бар

def get_repositories(project_name):
    """
    Получает список репозиториев в указанном проекте и возвращает объекты с полями .id и .name.
    """
    try:
        connection = connect_to_azure()
        git_client = connection.clients.get_git_client()
        
        log(f"Запрос списка репозиториев для проекта {project_name}...")
        repos = git_client.get_repositories(project=project_name)

        if not repos:
            log(f"Нет репозиториев в проекте {project_name}.", level="WARNING")
            return []

        repo_list = [repo for repo in repos if isinstance(repo, GitRepository)]
        log(f"Получено {len(repo_list)} репозиториев: {[repo.name for repo in repo_list]}")
        return repo_list  # Возвращаем список объектов, а не просто имена

    except Exception as e:
        log(f"Ошибка при получении репозиториев: {str(e)}", level="ERROR")
        return []

def get_repo_files(project_name, repository_name):
    """Получает список файлов в репозитории через API Azure DevOps."""
    try:
        connection = connect_to_azure()
        git_client = connection.clients.get_git_client()
        
        log(f"Получение списка файлов для репозитория {repository_name}...")
        items = git_client.get_items(repository_name, project=project_name, recursion_level="Full")

        file_paths = [item.path for item in items if not item.is_folder]
        log(f"Найдено файлов: {len(file_paths)}")
        return file_paths

    except Exception as e:
        log(f"Ошибка при получении списка файлов: {e}", level="ERROR")
        return []

def get_file_content(project_name, repository_name, file_path):
    """Загружает содержимое файла по его пути через API Azure DevOps."""
    try:
        connection = connect_to_azure()
        git_client = connection.clients.get_git_client()

        log(f"Загрузка файла {file_path} из репозитория {repository_name}...")
        content_generator = git_client.get_item_content(repository_name, path=file_path, project=project_name)

        # Корректно извлекаем данные из генератора
        file_content = b"".join(content_generator).decode("utf-8", errors="ignore")

        return file_content if file_content else ""

    except Exception as e:
        log(f"Ошибка при загрузке файла {file_path}: {e}", level="ERROR")
        return ""

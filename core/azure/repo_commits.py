from azure.devops.v7_0.git.models import GitQueryCommitsCriteria
from core.logging.logger import log

def get_all_commits(connection, project_name, repository_name):
    """
    Получает список коммитов из указанного репозитория.
    """
    try:
        git_client = connection.clients.get_git_client()

        # Получаем репозиторий по имени
        repositories = git_client.get_repositories(project_name)
        repository_id = next((repo.id for repo in repositories if repo.name == repository_name), None)

        if not repository_id:
            log(f"Репозиторий {repository_name} не найден в проекте {project_name}.", level="ERROR")
            return []

        # Запрос на получение коммитов
        search_criteria = GitQueryCommitsCriteria()
        all_commits = git_client.get_commits(
            repository_id=repository_id,
            project=project_name,
            search_criteria=search_criteria
        )

        log(f"Получено {len(all_commits)} коммитов из репозитория {repository_name}.")
        return all_commits

    except Exception as e:
        log(f"Ошибка при получении коммитов: {str(e)}", level="ERROR")
        return []

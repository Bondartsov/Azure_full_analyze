from core.azure.connection import connect_to_azure
from core.logging.logger import log
from azure.devops.v7_0.git.models import GitQueryCommitsCriteria  # Импортируем критерии поиска коммитов


def get_all_commits(project_name, repository):
    """
    Получает ВСЕ коммиты из репозитория, используя постраничную загрузку.
    """
    try:
        log(f"Начало получения коммитов для проекта {project_name}, репозитория {repository.name}")
        connection = connect_to_azure()
        git_client = connection.clients.get_git_client()

        # Получаем ID репозитория
        repository_id = repository.id

        # Запрашиваем коммиты с постраничной загрузкой
        all_commits = []
        batch_size = 500
        skip = 0

        search_criteria = GitQueryCommitsCriteria()  # Создаем объект критериев поиска

        while True:
            commits = list(git_client.get_commits(
                repository_id=repository_id,
                project=project_name,
                search_criteria=search_criteria,  # Передаем критерии поиска
                top=batch_size,
                skip=skip
            ))

            if not commits:
                break

            all_commits.extend(commits)
            skip += batch_size

            log(f"Загружено {len(commits)} коммитов, всего {len(all_commits)}")

        log(f"Всего получено {len(all_commits)} коммитов для {repository.name}")
        return all_commits

    except Exception as e:
        log(f"Ошибка при получении коммитов: {str(e)}", level="ERROR")
        return []


def get_last_commit(project_name, repository_name):
    """
    Получает хэш последнего коммита для репозитория.
    """
    try:
        log(f"Получение последнего коммита для проекта {project_name}, репозитория {repository_name}")
        connection = connect_to_azure()
        git_client = connection.clients.get_git_client()

        # Запрос на получение последнего коммита
        search_criteria = GitQueryCommitsCriteria()
        commits = git_client.get_commits(
            repository_id=repository_name,
            project=project_name,
            search_criteria=search_criteria,
            top=1
        )

        if commits:
            last_commit_id = commits[0].commit_id
            log(f"Последний коммит для {repository_name}: {last_commit_id}")
            return last_commit_id

        log(f"⚠ Нет коммитов в репозитории {repository_name}", level="WARNING")
        return None

    except Exception as e:
        log(f"Ошибка при получении последнего коммита: {e}", level="ERROR")
        return None

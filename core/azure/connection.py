# core/azure/connection.py
import configparser
import os
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

def connect_to_azure():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), '../../config/settings.ini'))

    org_url = config['AZURE_DEVOPS']['ORG_URL']
    access_token = config['AZURE_DEVOPS']['ACCESS_TOKEN']

    credentials = BasicAuthentication('', access_token)
    return Connection(base_url=org_url.rstrip('/') + '/', creds=credentials)

# core/azure/projects.py
def get_projects(connection):
    try:
        core_client = connection.clients.get_core_client()
        projects = core_client.get_projects()
        return [project.name for project in projects]
    except Exception as e:
        print(f"Ошибка при получении проектов: {str(e)}")
        return []

# core/azure/repos.py
def get_repositories(connection, project_name):
    try:
        git_client = connection.clients.get_git_client()
        repos = git_client.get_repositories(project_name)
        return [repo.name for repo in repos]
    except Exception as e:
        print(f"Ошибка при получении репозиториев: {str(e)}")
        return []

# core/azure/commits.py
def get_all_commits(connection, project_name, repository_name):
    try:
        git_client = connection.clients.get_git_client()
        repository_id = None
        
        # Поиск репозитория по имени
        repositories = git_client.get_repositories(project_name)
        for repo in repositories:
            if repo.name == repository_name:
                repository_id = repo.id
                break

        if not repository_id:
            print(f"Репозиторий {repository_name} не найден в проекте {project_name}.")
            return []

        # Получение коммитов
        all_commits = []
        batch_size = 100
        skip = 0

        while True:
            commits = git_client.get_commits(
                repository_id=repository_id,
                project=project_name,
                top=batch_size,
                skip=skip
            )
            all_commits.extend(commits)

            if len(commits) < batch_size:
                break

            skip += batch_size

        return all_commits

    except Exception as e:
        print(f"Ошибка при получении коммитов: {str(e)}")
        return []
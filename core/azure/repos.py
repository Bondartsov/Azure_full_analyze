# core/azure/repos.py
def get_repositories(connection, project_name):
    try:
        git_client = connection.clients.get_git_client()
        repos = git_client.get_repositories(project_name)
        return [repo.name for repo in repos]
    except Exception as e:
        print(f"Ошибка при получении репозиториев: {str(e)}")
        return []

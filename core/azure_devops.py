import sys
import os
import configparser
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_0.git.models import GitQueryCommitsCriteria

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'core')))

def get_config():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), '../config/settings.ini')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Файл настроек не найден: {config_path}")
    config.read(config_path)
    return config

def connect_to_azure():
    config = get_config()
    credentials = BasicAuthentication('', config['AZURE_DEVOPS']['ACCESS_TOKEN'])
    return Connection(
        base_url=config['AZURE_DEVOPS']['ORG_URL'].rstrip('/') + '/',
        creds=credentials
    )

def get_projects():
    try:
        connection = connect_to_azure()
        core_client = connection.clients.get_core_client()
        projects = core_client.get_projects()
        return [project.name for project in projects]
    except Exception as e:
        print(f"Ошибка при получении проектов: {str(e)}")
        return []

def get_repositories(project_name):
    try:
        connection = connect_to_azure()
        git_client = connection.clients.get_git_client()
        repos = git_client.get_repositories(project_name)
        return [repo.name for repo in repos]
    except Exception as e:
        print(f"Ошибка при получении репозиториев: {str(e)}")
        return []

def get_all_commits(git_client, repository_id, project_name, search_criteria):
    all_commits = []
    batch_size = 100
    skip = 0
    while True:
        try:
            commits = git_client.get_commits(
                repository_id=repository_id,
                project=project_name,
                search_criteria=search_criteria,
                top=batch_size,
                skip=skip
            )
            all_commits.extend(commits)
            if len(commits) < batch_size:
                break
            skip += batch_size
        except Exception as e:
            print(f"Ошибка при получении коммитов: {str(e)}")
            break
    return all_commits

def print_commits(commits):
    if not commits:
        print("Нет коммитов для отображения.")
        return
    print("\nСписок коммитов:\n")
    for i, commit in enumerate(commits, start=1):
        comment = commit.comment[:50] + "..." if len(commit.comment) > 50 else commit.comment
        date = commit.author.date.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{i}. Автор: {commit.author.name}, Дата: {date}, Коммит: {comment}")

def analyze_commits(commits):
    analysis = {
        'total_commits': len(commits),
        'top_authors': {}
    }
    for commit in commits:
        author = commit.author.name
        if author in analysis['top_authors']:
            analysis['top_authors'][author] += 1
        else:
            analysis['top_authors'][author] = 1
    sorted_authors = sorted(analysis['top_authors'].items(), key=lambda x: x[1], reverse=True)
    analysis['top_authors'] = sorted_authors
    return analysis

def print_analysis(analysis):
    print("\nАнализ коммитов:")
    print(f"Всего коммитов: {analysis['total_commits']}")
    print("Топ авторов:")
    for author, count in analysis['top_authors']:
        print(f"  - {author}: {count} коммитов")

def main():
    # Пример данных
    repositories = [
        {"id": 1, "name": "ST.CPM.Infrastructure"},
        {"id": 2, "name": "ST.CPM"},
        {"id": 3, "name": "wiki.description"},
        {"id": 4, "name": "TestApp"},
        {"id": 5, "name": "ST.CPM.Back"},
        {"id": 6, "name": "ST.CPM.Back.Cube"},
        {"id": 7, "name": "ST.CPM.Front"}
    ]

    # Вывод списка репозиториев
    print("Репозитории:")
    for i, repo in enumerate(repositories, start=1):
        print(f"{i}. {repo['name']}")

    # Выбор репозитория
    choice = int(input("Выберите репозиторий (введите номер): "))
    if 1 <= choice <= len(repositories):
        repository = repositories[choice - 1]
        print(f"[LOG] Выбран репозиторий: {repository['name']}")
        repository_id = repository['id']
        print(f"[LOG] ID репозитория: {repository_id}")
    else:
        print("[ERROR] Неверный выбор.")

if __name__ == "__main__":
    main()
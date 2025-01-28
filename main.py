from core.azure_devops import get_projects, get_repositories, get_all_commits, connect_to_azure
from core.analyze import analyze_commits
from core.report import generate_report
from core.logging import log
from azure.devops.v7_0.git.models import GitQueryCommitsCriteria

def main():
    log("Запуск приложения...")

    # Получение списка проектов
    projects = get_projects()
    print("Доступные проекты:", projects)
    if not projects:
        print("Нет доступных проектов.")
        return

    print("Доступные проекты:")
    for i, project in enumerate(projects, start=1):
        print(f"{i}. {project}")

    # Выбор проекта
    while True:
        try:
            project_choice = int(input("Выберите проект (введите номер): "))
            if 1 <= project_choice <= len(projects):
                project_name = projects[project_choice - 1]
                break
            else:
                print("Неверный номер. Попробуйте снова.")
        except ValueError:
            print("Пожалуйста, введите число.")

    log(f"Выбран проект: {project_name}")

    # Проверка репозиториев для каждого проекта
    for project in projects:
        repositories = get_repositories(project)
        print(f"Репозитории в проекте '{project}':", repositories)

    # Получение репозиториев
    repositories = get_repositories(project_name)
    if not repositories:
        print(f"Нет доступных репозиториев в проекте {project_name}.")
        return

    print(f"Репозитории в проекте '{project_name}':")
    for i, repo in enumerate(repositories, start=1):
        print(f"{i}. {repo}")

    # Выбор репозитория
    while True:
        try:
            repo_choice = int(input("Выберите репозиторий (введите номер): "))
            if 1 <= repo_choice <= len(repositories):
                repository_name = repositories[repo_choice - 1]
                break
            else:
                print("Неверный номер. Попробуйте снова.")
        except ValueError:
            print("Пожалуйста, введите число.")

    log(f"Выбран репозиторий: {repository_name}")

    # Установка соединения с Azure DevOps
    connection = connect_to_azure()
    git_client = connection.clients.get_git_client()

    # Получение списка репозиториев
    repositories = get_repositories(project_name)
    print("Репозитории:", repositories)

    # Поиск репозитория по имени
    repository = next((repo for repo in repositories if repo == repository_name), None)
    if not repository:
        print(f"Репозиторий '{repository_name}' не найден в проекте '{project_name}'.")
        return

    # Используем название репозитория как его ID
    repository_id = repository_name

    # Задание критериев поиска коммитов
    search_criteria = GitQueryCommitsCriteria()

    # Получение коммитов
    commits = get_all_commits(git_client, repository_id, project_name, search_criteria)
    if not commits:
        print(f"Нет коммитов в репозитории {repository_name}.")
        return

    print(f"Найдено {len(commits)} коммитов в репозитории {repository_name}.")

    # Анализ коммитов
    analysis = analyze_commits(commits)
    print("Анализ коммитов:", analysis)

    # Генерация отчёта
    generate_report(project_name, repository_name, analysis)

if __name__ == "__main__":
    main()
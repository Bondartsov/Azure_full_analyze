import logging  # Добавляем импорт
from core.azure.connection import connect_to_azure
from core.azure.projects import get_projects
from core.azure.repos import get_repositories
from core.azure.repo_commits import get_all_commits
from core.analyze.commit_analysis import analyze_commits
from core.reports.generate import generate_report
from core.utils.common import choose_from_list
from core.logging.logger import log

def main():
    log("Запуск приложения...")

    # Подключение к Azure DevOps
    connection = connect_to_azure()
    if not connection:
        log("Не удалось подключиться к Azure DevOps.", level=logging.ERROR)
        return

    # Получение и выбор проекта
    projects = get_projects(connection)
    if not projects:
        log("Нет доступных проектов.", level=logging.WARNING)
        return

    project_name = choose_from_list(projects, "Выберите проект")
    log(f"Выбран проект: {project_name}")

    # Получение и выбор репозитория
    repositories = get_repositories(connection, project_name)
    if not repositories:
        log(f"Нет репозиториев в проекте {project_name}.", level=logging.WARNING)
        return

    repository_name = choose_from_list(repositories, "Выберите репозиторий")
    log(f"Выбран репозиторий: {repository_name}")

    # Получение и анализ коммитов
    commits = get_all_commits(connection, project_name, repository_name)
    if not commits:
        log(f"Нет коммитов в репозитории {repository_name}.", level=logging.WARNING)
        return

    log(f"Найдено {len(commits)} коммитов в репозитории {repository_name}.")
    analysis = analyze_commits(commits)

    # Генерация отчёта
    generate_report(project_name, repository_name, analysis)
    log("Работа завершена. Отчёт сохранён.")

if __name__ == "__main__":
    main()

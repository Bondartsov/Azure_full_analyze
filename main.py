import os
from core.azure.connection import connect_to_azure
from core.azure.projects import get_projects
from core.azure.repos import get_repositories
from core.azure.repo_commits import get_all_commits
from core.analyze.commit_analysis import analyze_commits
from core.reports.generate import generate_report
from core.utils.common import choose_from_list
from core.logging.logger import log
from core.utils.token_counter import count_tokens_in_repo

def main():
    log("Запуск приложения...")

    # Получение и выбор проекта
    projects = get_projects()
    log(f"Получены проекты: {projects}")
    if not projects:
        log("Нет доступных проектов.", level="WARNING")
        return

    project_name = choose_from_list(projects, "Выберите проект")
    log(f"Выбран проект: {project_name}")

    # Получение списка репозиториев
    repositories = get_repositories(project_name)
    log(f"Получены репозитории: {repositories}")
    if not repositories:
        log(f"Нет репозиториев в проекте {project_name}.", level="WARNING")
        return

    repository = choose_from_list(repositories, "Выберите репозиторий")
    log(f"Выбран репозиторий: {repository.name}")

    # Подсчёт токенов
    log(f"Начало подсчёта токенов в репозитории {repository.name}...")
    result = count_tokens_in_repo(project_name, repository.name)

    if isinstance(result, tuple):
        token_data, total_tokens = result
    else:
        total_tokens = result
        token_data = {}

    log(f"Подсчёт токенов завершён. Всего токенов: {total_tokens}")

    # Получение и анализ коммитов
    log(f"Начало получения коммитов для проекта {project_name}, репозитория {repository.name}")
    commits = get_all_commits(project_name, repository.name)
    
    if commits is None:
        log(f"Ошибка при получении коммитов. Репозиторий {repository.name} недоступен.", level="ERROR")
        return

    log(f"Получены коммиты: {len(commits)}")
    if not commits:
        log(f"Нет коммитов в репозитории {repository.name}.", level="WARNING")
        return

    analysis = analyze_commits(commits)
    log(f"Результат анализа: {analysis}")

    # Генерация отчёта
    log("Начало генерации отчёта...")
    report_path = generate_report(project_name, repository.name, analysis, total_tokens)
    log(f"Отчёт успешно сохранён: {report_path}")

if __name__ == "__main__":
    main()

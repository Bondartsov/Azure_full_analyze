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

def format_number(number):
    """Форматирует числа с пробелами (1000000 -> 1 000 000)"""
    return f"{number:,}".replace(",", " ")

def analyze_repository(project_name, repository):
    """Функция анализа одного репозитория"""
    repository_name = repository.name
    log(f"Начало анализа репозитория: {repository_name}")

    # Подсчёт токенов
    log(f"📊 Начало подсчёта токенов в {repository_name}...")
    token_data, total_tokens = count_tokens_in_repo(project_name, repository_name)
    log(f"✅ Подсчёт токенов завершён: {format_number(total_tokens)} токенов")

    # Получение коммитов
    log(f"🔄 Получение коммитов для {repository_name}...")
    commits = get_all_commits(project_name, repository_name)

    if commits is None:
        log(f"⚠ Ошибка при получении коммитов для {repository_name}", level="ERROR")
        return

    log(f"📌 Найдено {format_number(len(commits))} коммитов")

    # Анализ коммитов
    analysis = analyze_commits(commits) if commits else {"total_commits": 0, "top_authors": []}
    log(f"📊 Анализ завершён: {analysis}")

    # Генерация отчёта
    log("📄 Генерация отчёта...")
    report_path = generate_report(project_name, repository_name, total_tokens, commits, analysis)

    if report_path:
        log(f"✅ Отчёт сохранён: {report_path}")
        print(f"\n✅ Репозиторий {repository_name}: Коммитов: {format_number(len(commits))}, Токенов: {format_number(total_tokens)}")
        print(f"📄 Отчёт сохранён: {report_path}")
    else:
        log("❌ Ошибка при генерации отчёта!", level="ERROR")
        print("\n❌ Ошибка при генерации отчёта!")

def main():
    log("🚀 Запуск приложения...")

    # Получение и выбор проекта
    projects = get_projects()
    log(f"📌 Доступные проекты: {projects}")
    if not projects:
        log("⚠ Нет доступных проектов.", level="WARNING")
        return

    project_name = choose_from_list(projects, "Выберите проект")
    log(f"✅ Выбран проект: {project_name}")

    # Получение списка репозиториев
    repositories = get_repositories(project_name)
    log(f"📌 Найдено {format_number(len(repositories))} репозиториев.")
    if not repositories:
        log(f"⚠ Нет репозиториев в проекте {project_name}.", level="WARNING")
        return

    # Выбор между анализом всех или конкретного репозитория
    options = ["📂 Анализировать все репозитории"] + [repo.name for repo in repositories]
    selected_option = choose_from_list(options, "Выберите действие")

    if selected_option == "📂 Анализировать все репозитории":
        log(f"📊 Начат анализ всех репозиториев проекта {project_name}...")
        for repository in repositories:
            analyze_repository(project_name, repository)
        log(f"✅ Анализ всех репозиториев проекта {project_name} завершён!")
    else:
        repository = next(repo for repo in repositories if repo.name == selected_option)
        analyze_repository(project_name, repository)

if __name__ == "__main__":
    main()

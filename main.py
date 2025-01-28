import os
from core.azure.connection import connect_to_azure
from core.azure.projects import get_projects
from core.azure.repos import get_repositories
from core.azure.repo_commits import get_all_commits, get_last_commit
from core.analyze.commit_analysis import analyze_commits
from core.reports.generate import generate_report
from core.reports.summary import generate_summary
from core.utils.cache import is_repo_changed, load_repo_data_from_cache, save_repo_data_to_cache
from core.utils.common import choose_from_list
from core.logging.logger import log
from core.utils.token_counter import count_tokens_in_repo
from tqdm import tqdm


def format_number(number):
    """Форматирует числа с пробелами (1000000 -> 1 000 000)"""
    return f"{number:,}".replace(",", " ")


def analyze_repository(project_name, repository, progress_bar):
    """Функция анализа одного репозитория"""
    repository_name = repository.name
    progress_bar.set_description(f"🔍 Анализ: {repository_name}")
    log(f"📂 Начало анализа репозитория: {repository_name}")

    # Получаем последний коммит
    latest_commit = get_last_commit(project_name, repository_name)

    # Проверяем изменения в репозитории
    repo_changed = is_repo_changed(project_name, repository_name, latest_commit)

    if not repo_changed:
        cached_data = load_repo_data_from_cache(project_name, repository_name)
        if cached_data:
            total_tokens, commit_count = cached_data
            if total_tokens > 0:  # 🔹 Проверяем, есть ли нормальные данные
                log(f"✅ Используем закэшированные данные для {repository_name}: {format_number(total_tokens)} токенов, {format_number(commit_count)} коммитов")
                
                # Генерация отчёта из кэша
                report_path = generate_report(project_name, repository_name, total_tokens, [], {"total_commits": commit_count, "top_authors": []})
                log(f"📄 Отчёт из кэша сохранён: {report_path}")

                progress_bar.update(1)
                return {"repository": repository_name, "tokens": total_tokens, "commits": commit_count, "cached": True}
            else:
                log(f"⚠ Кэш для {repository_name} пустой или некорректный, пересчитываем.")

    # Подсчёт токенов
    log(f"📊 Подсчёт токенов в {repository_name}...")
    token_data, total_tokens = count_tokens_in_repo(project_name, repository_name)
    log(f"✅ Подсчёт токенов завершён: {format_number(total_tokens)} токенов")

    # Получение коммитов
    log(f"🔄 Получение коммитов для {repository_name}...")
    commits = get_all_commits(project_name, repository_name)

    if commits is None:
        log(f"⚠ Ошибка при получении коммитов для {repository_name}", level="ERROR")
        progress_bar.update(1)
        return None

    log(f"📌 Найдено {format_number(len(commits))} коммитов")

    # Анализ коммитов
    analysis = analyze_commits(commits) if commits else {"total_commits": 0, "top_authors": []}
    log(f"📊 Анализ завершён: {analysis}")

    # Генерация отчёта
    log("📄 Генерация отчёта...")
    report_path = generate_report(project_name, repository_name, total_tokens, commits, analysis)

    if report_path:
        log(f"✅ Отчёт сохранён: {report_path}")
        save_repo_data_to_cache(project_name, repository_name, total_tokens, len(commits))  # 🔹 Сохранение в кэш
        progress_bar.update(1)
        return {"repository": repository_name, "tokens": total_tokens, "commits": len(commits), "cached": False}
    else:
        log("❌ Ошибка при генерации отчёта!", level="ERROR")
        progress_bar.update(1)
        return None


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

    repository_results = []
    if selected_option == "📂 Анализировать все репозитории":
        log(f"📊 Начат анализ всех репозиториев проекта {project_name}...")

        with tqdm(total=len(repositories), desc="⏳ Обработка репозиториев", unit="репо") as progress_bar:
            for repository in repositories:
                result = analyze_repository(project_name, repository, progress_bar)
                if result:
                    repository_results.append(result)

        # Генерация сводного отчёта
        if repository_results:
            summary_path = generate_summary(project_name, repository_results)
            if summary_path:
                log(f"📄 Сводный отчёт сохранён: {summary_path}")
                print(f"\n📄 Сводный отчёт создан: {summary_path}")
        else:
            log(f"⚠ Не удалось создать сводный отчёт: нет обработанных репозиториев.", level="WARNING")

        log(f"✅ Анализ всех репозиториев проекта {project_name} завершён!")
    else:
        repository = next((repo for repo in repositories if repo.name == selected_option), None)
        if not repository:
            log(f"❌ Ошибка: репозиторий {selected_option} не найден.", level="ERROR")
            return

        with tqdm(total=1, desc=f"🔍 Анализ: {repository.name}", unit="репо") as progress_bar:
            analyze_repository(project_name, repository, progress_bar)


if __name__ == "__main__":
    main()

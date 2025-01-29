from core.utils.common import select_project, select_repositories
from core.analyze.repository_analysis import analyze_repository
from core.analyze.batch_analysis import analyze_all_repositories
from core.logging.logger import log


def main():
    log("🚀 Запуск приложения...")
    print("🚀 Запуск приложения...", flush=True)

    # Выбор проекта
    project_name = select_project()
    if not project_name:
        return

    # Выбор репозиториев (все или один)
    repositories, single_repository = select_repositories(project_name)
    if not repositories and not single_repository:
        return

    # Запуск анализа
    if repositories:
        analyze_all_repositories(project_name, repositories)
    else:
        analyze_repository(project_name, single_repository, progress_bar=None)
    
    print(f"🎉 Анализ завершён для {project_name}", flush=True)
    log(f"🎉 Анализ завершён для {project_name}")


if __name__ == "__main__":
    main()

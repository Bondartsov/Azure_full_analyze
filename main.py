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
        log("❌ Проект не выбран. Завершение работы.", level="ERROR")
        print("❌ Проект не выбран. Завершение работы.", flush=True)
        return

    # Выбор репозиториев (все или один)
    repositories, single_repository = select_repositories(project_name)

    if not repositories and not single_repository:
        log("❌ Репозитории не выбраны. Завершение работы.", level="ERROR")
        print("❌ Репозитории не выбраны. Завершение работы.", flush=True)
        return

    # Запуск анализа
    if repositories:
        print(f"[DEBUG] Старт анализа, выбран проект: {project_name}, Кол-во репозиториев: {len(repositories)}", flush=True)
        analyze_all_repositories(project_name, repositories)
    else:
        print(f"[DEBUG] Старт анализа одного репозитория: {single_repository.name}", flush=True)
        analyze_repository(project_name, single_repository, progress_bar=None)
    
    print(f"🎉 Анализ завершён для {project_name}", flush=True)
    log(f"🎉 Анализ завершён для {project_name}")

if __name__ == "__main__":
    main()

from core.utils.common import select_project, select_repositories
from core.analyze.repository_analysis import analyze_repository
from core.analyze.batch_analysis import analyze_all_repositories
from core.logging.logger import log
from core.utils.cache import clear_project_summary_cache, clear_cache_for_repo

def main():
    log("🚀 Запуск приложения...")
    print("🚀 Запуск приложения...", flush=True)

    # 1. Выбор проекта
    project_name = select_project()
    if not project_name:
        log("❌ Проект не выбран. Завершение работы.", level="ERROR")
        print("❌ Проект не выбран. Завершение работы.", flush=True)
        return

    # 2. Выбор репозиториев (все или один)
    repositories, single_repository = select_repositories(project_name)

    if not repositories and not single_repository:
        log("❌ Репозитории не выбраны. Завершение работы.", level="ERROR")
        print("❌ Репозитории не выбраны. Завершение работы.", flush=True)
        return

    # 3a. Если выбраны ВСЕ репозитории:
    if repositories:
        # Предложение очистить кэш всего проекта
        print(f"\nОчистить кэш проекта {project_name}?")
        print("1. Да")
        print("2. Нет")
        choice = input("Введите номер: ").strip()

        if choice == "1":
            clear_project_summary_cache(project_name)
            log(f"🗑️ Кэш очищен для проекта {project_name}")
            print(f"🗑️ Кэш очищен для проекта: {project_name}\n")

        print(f"[DEBUG] Старт анализа, выбран проект: {project_name}, Кол-во репозиториев: {len(repositories)}", flush=True)
        analyze_all_repositories(project_name, repositories)

    # 3b. Если выбран ОДИН репозиторий:
    else:
        repo_name = single_repository.name
        # Предложение очистить кэш одного репозитория
        print(f"\nОчистить кэш репозитория {repo_name}?")
        print("1. Да")
        print("2. Нет")
        choice = input("Введите номер: ").strip()

        if choice == "1":
            clear_cache_for_repo(project_name, repo_name)
            log(f"🗑️ Кэш очищен для репозитория {repo_name}")
            print(f"🗑️ Кэш очищен для репозитория: {repo_name}\n")

        print(f"[DEBUG] Старт анализа одного репозитория: {repo_name}", flush=True)
        analyze_repository(project_name, single_repository, repo_changed=True)  
        # ↑ Если в твоём коде не используется 3-й аргумент, удали его

    # По окончании
    print(f"🎉 Анализ завершён для {project_name}", flush=True)
    log(f"🎉 Анализ завершён для {project_name}")


if __name__ == "__main__":
    main()

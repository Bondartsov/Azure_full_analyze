# main.py
from core.utils.common import select_project, select_repositories
from core.analyze.repository_analysis import analyze_repository
from core.analyze.batch_analysis import analyze_all_repositories
from core.logging.logger import log
from core.utils.cache import clear_project_summary_cache, clear_cache_for_repo
from dotenv import load_dotenv
load_dotenv()

# Теперь переменные из .env доступны через os.getenv()

def choose_analysis_mode() -> str:
    """
    Запрашивает выбор типа анализа:
      1. Быстрый анализ
      2. Глубокий ИИ анализ (быстрый + вызов ИИ)
    Возвращает "fast" или "deep".
    """
    while True:
        print("\nВыберите тип анализа:")
        print("1. Быстрый анализ")
        print("2. Глубокий ИИ анализ")
        choice = input("Введите 1 или 2: ").strip()
        if choice == "1":
            return "fast"
        elif choice == "2":
            return "deep"
        else:
            print("Неверный выбор, попробуйте снова.")

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

    # 3. Выбор типа анализа
    analysis_mode = choose_analysis_mode()
    print(f"\nВыбран тип анализа: {'Глубокий ИИ анализ' if analysis_mode == 'deep' else 'Быстрый анализ'}\n", flush=True)

    # 4. Запуск анализа
    # 4a. Если выбраны ВСЕ репозитории:
    if repositories:
        print(f"\nОчистить кэш проекта {project_name}?")
        print("1. Да")
        print("2. Нет")
        choice = input("Введите номер: ").strip()

        if choice == "1":
            clear_project_summary_cache(project_name)
            log(f"🗑️ Кэш очищен для проекта {project_name}")
            print(f"🗑️ Кэш очищен для проекта: {project_name}\n")

        print(f"[DEBUG] Старт анализа, выбран проект: {project_name}, Кол-во репозиториев: {len(repositories)}", flush=True)
        analyze_all_repositories(project_name, repositories, analysis_mode)

    # 4b. Если выбран ОДИН репозиторий:
    else:
        repo_name = single_repository.name
        print(f"\nОчистить кэш репозитория {repo_name}?")
        print("1. Да")
        print("2. Нет")
        choice = input("Введите номер: ").strip()

        if choice == "1":
            clear_cache_for_repo(project_name, repo_name)
            log(f"🗑️ Кэш очищен для репозитория {repo_name}")
            print(f"🗑️ Кэш очищен для репозитория: {repo_name}\n")

        print(f"[DEBUG] Старт анализа одного репозитория: {repo_name}", flush=True)
        # При одиночном анализе также передаём тип анализа
        analyze_repository(project_name, single_repository, repo_changed=True, analysis_mode=analysis_mode)

    print(f"🎉 Анализ завершён для {project_name}", flush=True)
    log(f"🎉 Анализ завершён для {project_name}")

if __name__ == "__main__":
    main()

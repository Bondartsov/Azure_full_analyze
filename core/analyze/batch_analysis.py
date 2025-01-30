import json
from core.analyze.repository_analysis import analyze_repository
from core.reports.summary import generate_summary
from core.logging.logger import log
from core.utils.cache import is_repo_changed

def analyze_all_repositories(project_name, repositories):
    """
    Анализирует все репозитории в проекте и создаёт сводный отчёт.
    Разные сообщения:
      - "<repo> взят из кэша", если repo_changed = False
      - "🔍 Идёт анализ <repo>..."  если repo_changed = True
    """
    repositories_count = len(repositories)
    log(f"📊 Начат анализ всех репозиториев проекта {project_name}...")

    # ---- Пустая строка, чтобы отделить вывод меню от анализа:
    print()

    # Верхний блок-«рамка»
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🔎 Старт анализа: проект «{project_name}», репозиториев: {repositories_count}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    repository_results = []

    for i, repository in enumerate(repositories, start=1):
        repository_name = repository.name

        # 1. Проверка, изменился ли репозиторий
        repo_changed = is_repo_changed(project_name, repository_name)

        # 2. Выводим, откуда берём данные — из кэша или анализ с нуля
        if not repo_changed:
            print(f"{repository_name} взят из кэша")
        else:
            print(f"🔍 Идёт анализ {repository_name}...")

        # 3. Запуск анализа, передаём признак изменения
        result = analyze_repository(project_name, repository, repo_changed)

        # 4. Итоги анализа
        if result:
            tokens_str = f"{result['tokens']:,}".replace(",", " ")
            print(f"💠Анализ {repository_name} завершён, количество токенов: {tokens_str}")

            # Отчёт (если хотим вывести)
            report_path = result.get("report_path")
            if report_path:
                print(f"📄 Отчёт анализа {repository_name} сохранён: {report_path}")

            repository_results.append(result)
        else:
            print(f"⚠ Анализ не дал результатов для {repository_name}")

        # 5. Прогресс анализа по всему проекту
        progress_percent = int((i / repositories_count) * 100)
        print(f"📈 Прогресс анализа проекта «{project_name}»: {progress_percent}%\n")

    # 6. Генерация сводного отчёта
    if repository_results:
        summary_path = generate_summary(project_name, repository_results)
        if summary_path:
            log(f"📄 Сводный отчёт сохранён: {summary_path}")
            print(f"📄 Сводный отчёт по проекту «{project_name}» создан: {summary_path}")
    else:
        log(f"⚠ Не удалось создать сводный отчёт: нет обработанных репозиториев.", level="WARNING")

    log(f"✅ Анализ всех репозиториев проекта {project_name} завершён!")
    print(f"✅ Анализ всех репозиториев проекта «{project_name}» завершён!")

# core/analyze/batch_analysis.py
import json
from core.analyze.repository_analysis import analyze_repository
from core.reports.summary import generate_summary
from core.logging.logger import log
from core.utils.cache import is_repo_changed

def analyze_all_repositories(project_name, repositories, analysis_mode="fast"):
    """
    Анализирует все репозитории в проекте с учетом выбранного типа анализа.
    Выводит сообщения о том, откуда берутся данные (из кэша или анализ с нуля).
    """
    repositories_count = len(repositories)
    log(f"📊 Начат анализ всех репозиториев проекта {project_name}...")

    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🔎 Старт анализа: проект «{project_name}», репозиториев: {repositories_count}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    repository_results = []

    for i, repository in enumerate(repositories, start=1):
        repository_name = repository.name
        repo_changed = is_repo_changed(project_name, repository_name)

        if analysis_mode == "fast":
            if not repo_changed:
                print(f"{repository_name} взят из кэша")
            else:
                print(f"🔍 Идёт анализ {repository_name}...")
        else:
            # При глубоком анализе всегда выполняем полный анализ
            print(f"🔍 Идёт глубокий анализ {repository_name}...")

        result = analyze_repository(project_name, repository, repo_changed, analysis_mode)
        if result:
            tokens_str = f"{result['tokens']:,}".replace(",", " ")
            print(f"💠 Анализ {repository_name} завершён, количество токенов: {tokens_str}")
            report_path = result.get("report_path")
            if report_path:
                print(f"📄 Отчёт анализа {repository_name} сохранён: {report_path}")
            repository_results.append(result)
        else:
            print(f"⚠ Анализ не дал результатов для {repository_name}")

        progress_percent = int((i / repositories_count) * 100)
        print(f"📈 Прогресс анализа проекта «{project_name}»: {progress_percent}%\n")

    if repository_results:
        summary_path = generate_summary(project_name, repository_results)
        if summary_path:
            log(f"📄 Сводный отчёт сохранён: {summary_path}")
            print(f"📄 Сводный отчёт по проекту «{project_name}» создан: {summary_path}")
    else:
        log("⚠ Не удалось создать сводный отчёт: нет обработанных репозиториев.", level="WARNING")

    log(f"✅ Анализ всех репозиториев проекта {project_name} завершён!")
    print(f"✅ Анализ всех репозиториев проекта «{project_name}» завершён!")

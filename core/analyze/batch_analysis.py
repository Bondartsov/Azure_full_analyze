from tqdm import tqdm
from core.analyze.repository_analysis import analyze_repository
from core.reports.summary import generate_summary
from core.logging.logger import log

def analyze_all_repositories(project_name, repositories):
    """
    Анализирует все репозитории в проекте и создаёт сводный отчёт.
    """
    log(f"📊 Начат анализ всех репозиториев проекта {project_name}...")

    repository_results = []
    with tqdm(total=len(repositories), desc="⏳ Общий анализ проекта", unit="репо") as progress_bar:
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

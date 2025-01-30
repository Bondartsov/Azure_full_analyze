## core/analyze/batch_analysis.py

from tqdm import tqdm
from core.analyze.repository_analysis import analyze_repository
from core.reports.summary import generate_summary
from core.logging.logger import log
from core.utils.cache import is_repo_changed
from core.azure.repo_commits import get_last_commit
import json

def analyze_all_repositories(project_name, repositories):
    """
    Анализирует все репозитории в проекте и создаёт сводный отчёт.
    """
    log(f"📊 Начат анализ всех репозиториев проекта {project_name}...")

    repository_results = []
    with tqdm(total=len(repositories), desc="⏳ Общий анализ проекта", unit="репо") as progress_bar:
        for repository in repositories:
            repository_name = repository.name

            # ✅ Получаем последний коммит перед проверкой кэша
            latest_commit = get_last_commit(project_name, repository_name)

            # ✅ Передаём `latest_commit` в `is_repo_changed`
            repo_changed = is_repo_changed(project_name, repository_name, latest_commit)

            # 📌 Отладочный вывод перед анализом
            print(f"\n[DEBUG] 🔍 Анализ репозитория: {repository_name}")
            print(f"   🔹 Изменился: {repo_changed}")
            print(f"   🔹 Последний коммит: {latest_commit}")

            result = analyze_repository(project_name, repository, progress_bar)

            if result:
                print(f"[DEBUG] ✅ Анализ завершён, данные:")
                print(json.dumps(result, indent=4, ensure_ascii=False))
                repository_results.append(result)
            else:
                print(f"[DEBUG] ❌ Анализ не дал результатов для {repository_name}")

    # Генерация сводного отчёта
    if repository_results:
        print(f"\n[DEBUG] 📊 Список результатов для сводного отчёта:")
        print(json.dumps(repository_results, indent=4, ensure_ascii=False))
        summary_path = generate_summary(project_name, repository_results)
        if summary_path:
            log(f"📄 Сводный отчёт сохранён: {summary_path}")
            print(f"\n📄 Сводный отчёт создан: {summary_path}")
    else:
        log(f"⚠ Не удалось создать сводный отчёт: нет обработанных репозиториев.", level="WARNING")

    log(f"✅ Анализ всех репозиториев проекта {project_name} завершён!")

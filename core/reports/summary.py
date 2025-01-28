import os
from core.logging.logger import log
from datetime import datetime

def format_number(number):
    """Форматирует числа с пробелами (1000000 -> 1 000 000)"""
    return f"{number:,}".replace(",", " ")

def generate_summary(project_name, repository_results):
    """Генерирует сводный отчёт по всем репозиториям проекта"""
    if not repository_results:
        log(f"⚠ Нет данных для сводного отчёта по проекту {project_name}.", level="WARNING")
        return None

    summary_dir = "reports"
    os.makedirs(summary_dir, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    summary_filename = f"summary_{project_name}_{date_str}.txt"
    summary_path = os.path.join(summary_dir, summary_filename)

    total_tokens = sum(repo["tokens"] for repo in repository_results)

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"📌 Сводный отчёт по проекту: {project_name}\n")
        f.write(f"📅 Дата: {date_str}\n\n")
        f.write("🔍 Анализированные репозитории:\n")

        for idx, repo in enumerate(repository_results, start=1):
            f.write(f"{idx}. {repo['repository']} — {format_number(repo['tokens'])} токенов\n")

        f.write("\n📊 Итог:\n")
        f.write(f"💡 Общее количество токенов в проекте: {format_number(total_tokens)}\n")

    log(f"✅ Сводный отчёт сохранён: {summary_path}")
    return summary_path

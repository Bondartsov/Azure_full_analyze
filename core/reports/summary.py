import os
from core.logging.logger import log

def format_number(number):
    """Форматирует числа с пробелами (1000000 -> 1 000 000)"""
    return f"{number:,}".replace(",", " ")

def generate_summary(project_name, repository_results):
    """
    Генерирует сводный отчёт по всем проанализированным репозиториям.
    """
    if not repository_results:
        log("⚠ Не найдено данных для создания сводного отчёта.", level="WARNING")
        return None

    summary_filename = f"summary_{project_name}_{get_timestamp()}.txt"
    summary_path = os.path.join("reports", summary_filename)

    total_tokens = sum(repo["tokens"] for repo in repository_results)
    
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"📄 Сводный отчёт по проекту: {project_name}\n")
        f.write(f"📅 Дата: {get_timestamp()}\n\n")
        f.write("📋 Анализированные репозитории:\n")

        for idx, repo in enumerate(repository_results, start=1):
            f.write(f"{idx}. {repo['repository']} — {format_number(repo['tokens'])} токенов\n")

        f.write("\n🟢 Итог:\n")
        f.write(f"📍 Общее количество токенов в проекте: {format_number(total_tokens)}\n")

    log(f"✅ Сводный отчёт сохранён: {summary_path}")
    return summary_path


def get_timestamp():
    """Возвращает текущее время в формате YYYY-MM-DD_HH-MM"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d_%H-%M")

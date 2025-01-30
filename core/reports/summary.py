# core/reports/summary.py

import os
from datetime import datetime
from core.reports.report_formatter import format_project_summary
from core.logging.logger import log

REPORTS_DIR = "reports"

def generate_summary(project_name, repositories_reports):
    """
    Генерирует сводный отчёт по проекту.
    :param project_name: Название проекта.
    :param repositories_reports: Список отчётов по репозиториям.
    :return: Путь к сохранённому файлу.
    """
    log(f"📄 Генерация сводного отчёта для проекта {project_name}...")

    if not repositories_reports or not isinstance(repositories_reports, list):
        log(f"⚠ Ошибка! Нет данных для сводного отчёта {project_name}.", level="ERROR")
        return None

    try:
        total_files = sum(len(repo.get("files", [])) for repo in repositories_reports if isinstance(repo, dict))
        total_lines = sum(sum(file.get("lines", 0) for file in repo.get("files", [])) for repo in repositories_reports if isinstance(repo, dict))
        total_comments = sum(sum(file.get("comments", 0) for file in repo.get("files", [])) for repo in repositories_reports if isinstance(repo, dict))
        total_tokens = sum(sum(file.get("tokens", 0) for file in repo.get("files", [])) for repo in repositories_reports if isinstance(repo, dict))

        # Обновляем количество токенов в репозиториях для корректного отображения
        for repo in repositories_reports:
            repo["tokens"] = sum(file.get("tokens", 0) for file in repo.get("files", []))

    except Exception as e:
        log(f"❌ Ошибка при обработке данных в generate_summary(): {e}", level="ERROR")
        return None

    # Формируем отчёт
    report_content = format_project_summary(project_name, repositories_reports)

    # Создаём папку для отчётов
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # Создаём имя файла с временной меткой
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    summary_filename = f"summary_{project_name}_{timestamp}.txt"
    summary_path = os.path.join(REPORTS_DIR, summary_filename)

    # Сохраняем TXT
    try:
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        log(f"✅ Сводный отчёт сохранён: {summary_path}")

    except Exception as e:
        log(f"❌ Ошибка при сохранении сводного отчёта: {e}", level="ERROR")
        return None

    return summary_path

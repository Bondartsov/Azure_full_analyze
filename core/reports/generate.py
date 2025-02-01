import os
from datetime import datetime
from core.reports.report_formatter import format_repository_report
from core.logging.logger import log

REPORTS_DIR = "reports"

def generate_report(project_name, repository_name, files_data):
    """
    Генерирует отчёт по репозиторию в папке:
      D:\Projects\Azure_full_analyze\reports\<project_name>\...
    """
    log(f"📄 Генерация отчёта для репозитория {repository_name}...")

    # Проверка
    if not isinstance(files_data, list):
        log(f"❌ Ошибка: files_data должен быть списком, но получен {type(files_data)}", level="ERROR")
        return None

    valid_files = [file for file in files_data if isinstance(file, dict)]
    if not valid_files:
        log(f"❌ Ошибка: Нет корректных данных о файлах для {repository_name}", level="ERROR")
        return None

    log(f"🔍 Проверено файлов: {len(files_data)}, допустимых: {len(valid_files)}")

    # Создаём подпапку для проекта
    project_report_dir = os.path.join(REPORTS_DIR, project_name)
    os.makedirs(project_report_dir, exist_ok=True)

    # Генерация текста
    report_content = format_repository_report(project_name, repository_name, valid_files)

    # Имя файла
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    report_filename = f"{project_name}_{repository_name}_report_{timestamp}.txt"
    report_path = os.path.join(project_report_dir, report_filename)

    # Сохраняем отчёт
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        log(f"✅ Отчёт сохранён: {report_path}")
    except Exception as e:
        log(f"❌ Ошибка при сохранении отчёта: {e}", level="ERROR")
        return None

    return report_path

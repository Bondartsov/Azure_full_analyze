import os
from datetime import datetime
from core.reports.report_formatter import format_repository_report
from core.logging.logger import log

REPORTS_DIR = "reports"

def generate_report(project_name, repository_name, files_data):
    """
    Генерирует отчёт по репозиторию.
    :param project_name: Название проекта.
    :param repository_name: Название репозитория.
    :param files_data: Данные о файлах в репозитории (список словарей).
    :return: Путь к сохранённому файлу.
    """
    log(f"📄 Генерация отчёта для репозитория {repository_name}...")

    # ✅ Проверка структуры `files_data`
    if not isinstance(files_data, list):
        log(f"❌ Ошибка: files_data должен быть списком, но получен {type(files_data)}", level="ERROR")
        return None

    # ✅ Фильтрация: оставляем только корректные элементы (словари)
    valid_files = [file for file in files_data if isinstance(file, dict)]

    if not valid_files:
        log(f"❌ Ошибка: Нет корректных данных о файлах для {repository_name}", level="ERROR")
        return None

    # ✅ Логируем отфильтрованные файлы
    log(f"🔍 Проверено файлов: {len(files_data)}, допустимых: {len(valid_files)}")

    # Создаём папку для отчётов
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # Генерируем отчёт
    report_content = format_repository_report(project_name, repository_name, valid_files)

    # Создаём имя файла с временной меткой
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    report_filename = f"{project_name}_{repository_name}_report_{timestamp}.txt"
    report_path = os.path.join(REPORTS_DIR, report_filename)

    # Сохраняем отчёт
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        log(f"✅ Отчёт сохранён: {report_path}")

    except Exception as e:
        log(f"❌ Ошибка при сохранении отчёта: {e}", level="ERROR")
        return None

    return report_path

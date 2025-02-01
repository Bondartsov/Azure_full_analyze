import os
from datetime import datetime
from core.ai.code_advisor import query_openai
from core.utils.token_counter import count_tokens_in_text
from core.logging.logger import log

REPORTS_DIR = "ai_reports"

def generate_ai_report(project_name, repository_name, folder_name, file_name, file_content):
    """
    Генерирует ИИ-отчёт по коду файла.
    """
    lines = file_content.split("\n")
    num_lines = len(lines)
    num_comments = sum(1 for line in lines if line.strip().startswith("#") or line.strip().startswith("//"))
    num_tokens = count_tokens_in_text(file_content)
    
    prompt = f"""
    Проанализируй следующий код:
    
    {file_content.encode("utf-8").decode("utf-8")}
    
    1. Определи структуру кода (функции, классы, импорты).
    2. Объясни, что делает этот код.
    3. Найди возможные ошибки или уязвимости.
    4. Насколько сложен этот код (1-10)?
    """.strip()
    
    analysis = query_openai(prompt)
    
    project_path = os.path.join(REPORTS_DIR, project_name, repository_name, folder_name)
    os.makedirs(project_path, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    report_filename = f"ai_report_{project_name}_{repository_name}_{folder_name}_{file_name}_{timestamp}.txt"
    report_path = os.path.join(project_path, report_filename)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"Проект: {project_name}\n")
        f.write(f"Репозиторий: {repository_name}\n")
        f.write(f"Папка: {folder_name}\n")
        f.write(f"Файл: {file_name}\n")
        f.write(f"Строк кода: {num_lines}\n")
        f.write(f"Комментариев: {num_comments}\n")
        f.write(f"Токенов: {num_tokens}\n\n")
        f.write("📌 **Анализ кода:**\n")
        f.write(analysis)
    
    print(f"DEBUG: Отчёт для файла {file_name} сохранён по пути: {report_path}", flush=True)
    return os.path.abspath(report_path)
def generate_deep_report_for_repo(project_name, repository_name, files_data):
    """
    Для глубокого анализа генерирует ИИ‑отчёты для каждого файла репозитория.
    Собирает пути созданных отчётов и формирует агрегированный сводный отчёт.
    Если ни один файл обработан, записывается сообщение об отсутствии файлов.
    После создания агрегированного отчёта его содержимое выводится в консоль.
    Возвращает абсолютный путь к агрегированному отчёту.
    """
    deep_report_paths = []
    for file_info in files_data:
        file_name = file_info.get("file_name") or file_info.get("path")
        folder = file_info.get("folder", "root")
        file_content = file_info.get("content")
        if not file_content:
            continue
        try:
            report_path = generate_ai_report(project_name, repository_name, folder, file_name, file_content)
            deep_report_paths.append(report_path)
        except Exception as e:
            log(f"❌ Ошибка генерации ИИ‑отчёта для файла {file_name}: {e}", level="ERROR")
    
    aggregated_dir = os.path.join(REPORTS_DIR, project_name, repository_name)
    os.makedirs(aggregated_dir, exist_ok=True)
    aggregated_report_path = os.path.join(aggregated_dir, "aggregated_deep_report.txt")
    try:
        with open(aggregated_report_path, "w", encoding="utf-8") as f:
            header = f"Агрегированный ИИ‑анализ для репозитория {repository_name}\n\n"
            f.write(header)
            if deep_report_paths:
                for path in deep_report_paths:
                    f.write(f"{path}\n")
            else:
                message = (
                    "Нет файлов для глубокого анализа, удовлетворяющих требованиям.\n"
                    "Проверьте настройки в .env (WHITE_EXTENSIONS) и наличие файлов в репозитории.\n"
                )
                f.write(message)
                print(message, flush=True)
        print(header, flush=True)
        with open(aggregated_report_path, "r", encoding="utf-8") as f:
            print(f.read(), flush=True)
    except Exception as e:
        log(f"❌ Ошибка при сохранении агрегированного ИИ‑отчёта: {e}", level="ERROR")
    return os.path.abspath(aggregated_report_path)
def get_deep_reports_for_repo(project_name, repository_name, files_data):
    """
    Возвращает список абсолютных путей к индивидуальным ИИ‑отчётам для каждого файла.
    """
    deep_reports = []
    for file_info in files_data:
        file_name = file_info.get("file_name") or file_info.get("path")
        folder = file_info.get("folder", "root")
        file_content = file_info.get("content")
        if not file_content:
            continue
        try:
            report_path = generate_ai_report(project_name, repository_name, folder, file_name, file_content)
            deep_reports.append(os.path.abspath(report_path))
        except Exception as e:
            log(f"❌ Ошибка генерации ИИ‑отчёта для файла {file_name}: {e}", level="ERROR")
    return deep_reports
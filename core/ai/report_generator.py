# core/ai/report_generator.py

import os
from datetime import datetime
from core.ai.code_advisor import query_openai
from core.utils.token_counter import count_tokens_in_text, split_text
from core.logging.logger import log

REPORTS_DIR = "ai_reports"

def generate_ai_report(project_name, repository_name, folder_name, file_name, file_content):
    """
    Генерирует ИИ-отчёт по коду файла.
    """
    lines = file_content.split("\n")
    num_lines = len(lines)
    num_comments = sum(1 for line in lines if line.strip().startswith("#") or line.strip().startswith("//"))
    num_tokens = count_tokens_in_text(file_content)  # Используем cl100k_base по умолчанию
    
    parts = split_text(file_content, max_tokens=3000)  # model по умолчанию 'cl100k_base'
    analyses = []
    
    for idx, part in enumerate(parts, 1):
        prompt = f"""
        Проанализируй следующий код:
        
        {part}
        
        1. Определи структуру кода (функции, классы, импорты).
        2. Объясни, что делает этот код.
        3. Найди возможные ошибки или уязвимости.
        4. Насколько сложен этот код (1-10)?
        """.strip()

        log(f"🚀 Отправка запроса в OpenAI для {file_name} (часть {idx})")

        analysis = query_openai(prompt)
        
        if analysis:
            analyses.append(analysis)
            log(f"📄 Получен анализ для части {idx} файла {file_name}")
        else:
            analyses.append("⚠️ Анализ не был получен от OpenAI.")
            log(f"⚠️ Анализ для части {idx} файла {file_name} пуст.", level="WARNING")
    
    aggregated_analysis = "\n\n---\n\n".join(analyses)
    
    project_path = os.path.join(REPORTS_DIR, project_name, repository_name, folder_name)
    os.makedirs(project_path, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    report_filename = f"ai_report_{file_name}_{timestamp}.txt"
    report_path = os.path.join(project_path, report_filename)

    log(f"📝 Сохранение отчёта: {report_path}")

    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"Проект: {project_name}\n")
            f.write(f"Репозиторий: {repository_name}\n")
            f.write(f"Папка: {folder_name}\n")
            f.write(f"Файл: {file_name}\n")
            f.write(f"Строк кода: {num_lines}\n")
            f.write(f"Комментариев: {num_comments}\n")
            f.write(f"Токенов: {num_tokens}\n\n")
            f.write("📌 **Анализ кода:**\n")
            f.write(aggregated_analysis)
        
        log(f"✅ Отчёт для файла {file_name} успешно создан: {report_path}")

        if not os.path.exists(report_path):
            log(f"❌ Ошибка: отчёт {report_path} не найден после сохранения!", level="ERROR")

        return os.path.abspath(report_path)

    except Exception as e:
        log(f"❌ Ошибка при сохранении отчёта для файла {file_name}: {e}", level="ERROR")
        return None

def generate_deep_report_for_repo(project_name, repository_name, files_data):
    """
    Генерирует ИИ-отчёты для каждого файла репозитория и собирает агрегированный отчёт.
    """
    log(f"🔍 Запуск глубокого ИИ-анализа для репозитория: {repository_name}")

    deep_report_paths = []
    
    for file_info in files_data:
        file_name = file_info.get("file_name") or file_info.get("path")
        folder = file_info.get("folder", "root")
        file_content = file_info.get("content")

        if not file_content:
            log(f"⚠️ Файл {file_name} пропущен: пустое содержимое.")
            continue
        
        log(f"📁 Начат анализ файла: {file_name}")

        try:
            # 🔥 Логирование перед вызовом функции
            log(f"🚀 Вызов generate_ai_report для файла: {file_name} (папка: {folder})")
            report_path = generate_ai_report(project_name, repository_name, folder, file_name, file_content)

            if report_path:
                deep_report_paths.append(report_path)
                log(f"✅ Файл {file_name} обработан, отчёт создан: {report_path}")
            else:
                log(f"❌ Не удалось создать отчёт для файла {file_name}!", level="ERROR")

        except Exception as e:
            log(f"❌ Ошибка генерации ИИ‑отчёта для файла {file_name}: {e}", level="ERROR")
    
    aggregated_dir = os.path.join(REPORTS_DIR, project_name, repository_name)
    os.makedirs(aggregated_dir, exist_ok=True)
    aggregated_report_path = os.path.join(aggregated_dir, "aggregated_deep_report.txt")

    log(f"📝 Сохранение агрегированного отчёта: {aggregated_report_path}")

    try:
        with open(aggregated_report_path, "w", encoding="utf-8") as f:
            header = f"Агрегированный ИИ-анализ для репозитория {repository_name}\n\n"
            f.write(header)
            if deep_report_paths:
                for path in deep_report_paths:
                    f.write(f"{path}\n")
            else:
                message = "⚠️ Нет файлов для глубокого анализа!"
                f.write(message)
        log(f"✅ Сохранён агрегированный отчёт: {aggregated_report_path}")
    except Exception as e:
        log(f"❌ Ошибка при сохранении агрегированного ИИ‑отчёта: {e}", level="ERROR")
    
    return os.path.abspath(aggregated_report_path)

def get_deep_reports_for_repo(project_name, repository_name, files_data):
    """
    Возвращает список абсолютных путей к индивидуальным ИИ-отчётам для каждого файла.
    """
    deep_reports = []
    for file_info in files_data:
        file_name = file_info.get("file_name") or file_info.get("path")
        folder = file_info.get("folder", "root")
        file_content = file_info.get("content")

        if not file_content:
            log(f"⚠️ Пропущен пустой файл: {file_name}")
            continue

        try:
            report_path = generate_ai_report(project_name, repository_name, folder, file_name, file_content)
            if report_path:
                deep_reports.append(os.path.abspath(report_path))
        except Exception as e:
            log(f"❌ Ошибка генерации ИИ-отчёта для файла {file_name}: {e}", level="ERROR")

    return deep_reports
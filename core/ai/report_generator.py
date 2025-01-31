import os
from datetime import datetime
from core.ai.code_advisor import query_openai
from core.utils.token_counter import count_tokens_in_text

REPORTS_DIR = "ai_reports"

def generate_ai_report(project_name, repository_name, folder_name, file_name, file_content):
    """
    Генерирует ИИ-отчёт по коду файла.
    """
    # Подсчитываем строки и комментарии
    lines = file_content.split("\n")
    num_lines = len(lines)
    num_comments = sum(1 for line in lines if line.strip().startswith("#") or line.strip().startswith("//"))

    # Подсчёт токенов
    num_tokens = count_tokens_in_text(file_content)

    # Формируем запрос к ИИ
    prompt = f"""
    Проанализируй следующий код:
    
    {file_content.encode("utf-8").decode("utf-8")}
    
    1. Определи структуру кода (функции, классы, импорты).
    2. Объясни, что делает этот код.
    3. Найди возможные ошибки или уязвимости.
    4. Насколько сложен этот код (1-10)?
    """.strip()

    analysis = query_openai(prompt)

    # Создаём папку для отчётов
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

    return report_path

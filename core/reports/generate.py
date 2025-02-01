import os
from datetime import datetime

def generate_report(project_name, repository_name, files_data):
    """
    Генерирует отчёт о быстром анализе репозитория.
    
    Формат отчёта:
    
    📂 Отчёт о быстром анализе репозитория: <repository_name>
    ====================================================================================
    📌 Проект: <project_name>
    📌 Репозиторий: <repository_name>
    ====================================================================================
    
    📊 Структура файлов:
    
    --------------------------------------------------------------------------------
    📂 <folder> - общее количество токенов: <folder_tokens>
    📄 <file_path> — <role> | 🔢 <lines> строк | 💬 <comments> комм. | 🏷 <tokens> токенов
    ...
    --------------------------------------------------------------------------------
    
    ====================================================================================
    📊 Итог по репозиторию: <repository_name>
    📜 Всего строк кода: <total_lines>
    💬 Всего комментариев: <total_comments>
    🏷 Всего токенов: <total_tokens>
    ====================================================================================
    """
    reports_dir = "reports"
    report_folder = os.path.join(reports_dir, project_name, repository_name)
    os.makedirs(report_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    report_filename = f"report_{repository_name}_{timestamp}.txt"
    report_path = os.path.join(report_folder, report_filename)
    
    # Группируем файлы по папке. Предполагаем, что файлы в files_data – словари с ключами:
    # "path" (или "file_name"), "lines", "comments", "tokens", "role"
    groups = {}
    total_lines = 0
    total_comments = 0
    total_tokens = 0
    
    for file_info in files_data:
        # Используем "path", если есть; иначе "file_name"
        path = file_info.get("path") or file_info.get("file_name") or "unknown"
        folder = os.path.dirname(path)
        # Если папка пустая, будем считать это корневой группой (отмечаем как пустую строку)
        if folder == "":
            folder = ""
        role = file_info.get("role", "Неизвестная роль")
        lines = file_info.get("lines", 0)
        comments = file_info.get("comments", 0)
        tokens = file_info.get("tokens", 0)
        total_lines += lines
        total_comments += comments
        total_tokens += tokens
        if folder not in groups:
            groups[folder] = {"files": [], "folder_tokens": 0}
        groups[folder]["files"].append({
            "path": path,
            "role": role,
            "lines": lines,
            "comments": comments,
            "tokens": tokens
        })
        groups[folder]["folder_tokens"] += tokens

    # Функция для форматирования чисел с разделителем пробелами (например, 1 337)
    def fmt_number(n):
        return "{:,.0f}".format(n).replace(",", " ")

    # Формируем заголовок отчёта
    header = f"📂 Отчёт о быстром анализе репозитория: {repository_name}\n"
    sep = "=" * 100
    header += f"\n{sep}\n"
    header += f"📌 Проект: {project_name}\n"
    header += f"📌 Репозиторий: {repository_name}\n"
    header += f"{sep}\n\n"
    header += "📊 Структура файлов:\n\n"
    
    group_texts = ""
    # Сортируем группы по имени папки (пустая строка для корневых файлов будет первой)
    for folder in sorted(groups.keys(), key=lambda x: (x != "", x)):
        folder_tokens = fmt_number(groups[folder]["folder_tokens"])
        group_header = "--------------------------------------------------------------------------------\n"
        if folder == "":
            group_header += f"📂  - общее количество токенов: {folder_tokens}\n"
        else:
            group_header += f"📂 {folder} - общее количество токенов: {folder_tokens}\n"
        group_header += "--------------------------------------------------------------------------------\n"
        file_lines = ""
        for f in groups[folder]["files"]:
            file_path = f["path"]
            file_role = f["role"]
            file_lines += (f"📄 {file_path} — {file_role} | 🔢 {fmt_number(f['lines'])} строк | "
                           f"💬 {fmt_number(f['comments'])} комм. | 🏷 {fmt_number(f['tokens'])} токенов\n")
        group_texts += group_header + file_lines + "--------------------------------------------------------------------------------\n"
    
    summary = f"{sep}\n"
    summary += f"📊 Итог по репозиторию: {repository_name}\n"
    summary += f"📜 Всего строк кода: {fmt_number(total_lines)}\n"
    summary += f"💬 Всего комментариев: {fmt_number(total_comments)}\n"
    summary += f"🏷 Всего токенов: {fmt_number(total_tokens)}\n"
    summary += f"{sep}\n"
    
    full_report = header + group_texts + summary
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(full_report)
    
    return os.path.abspath(report_path)

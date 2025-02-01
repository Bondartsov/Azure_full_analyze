import os
import json  # Для отладки

def format_repository_report(project_name, repository_name, files_data):
    """
    Форматирует отчёт для отдельного репозитория.
    """
    report_lines = [
        f"📂 Отчёт о быстром анализе репозитория: {repository_name}",
        "=" * 100,
        f"📌 Проект: {project_name}",
        f"📌 Репозиторий: {repository_name}",
        "=" * 100,
        "\n📊 Структура файлов:\n"
    ]

    # Если нет данных
    if not files_data:
        report_lines.append("⚠ Внимание: В репозитории нет данных для анализа (либо все файлы исключены).")
        report_lines.append("=" * 100)
        report_lines.append(f"📊 Итог по репозиторию: {repository_name}")
        report_lines.append("📜 Всего строк кода: 0")
        report_lines.append("🏷 Всего токенов: 0")
        report_lines.append("💬 Всего комментариев: 0")
        report_lines.append("=" * 100)
        return "\n".join(report_lines)

    # Группируем файлы по папкам
    folder_structure = {}
    for file_info in files_data:
        if "/" in file_info["path"]:
            folder, filename = file_info["path"].rsplit("/", 1)
        else:
            folder, filename = ("Корневая директория", file_info["path"])
        folder_structure.setdefault(folder, []).append((file_info["path"], filename, file_info))

    total_lines = 0
    total_tokens = 0
    total_comments = 0

    # Сортируем папки по имени
    for folder, files in sorted(folder_structure.items()):
        folder_tokens = sum(f[2].get("tokens", 0) for f in files)
        # Форматируем
        folder_tokens_str = f"{folder_tokens:,}".replace(",", " ")

        report_lines.append("--------------------------------------------------------------------------------")
        report_lines.append(f"📂 {folder} - общее количество токенов: {folder_tokens_str}")

        for full_path, filename, file_data in sorted(files, key=lambda x: x[0]):
            lines_ = file_data.get('lines', 0)
            tokens_ = file_data.get('tokens', 0)
            comments_ = file_data.get('comments', 0)
            role_ = file_data.get('role', "Неизвестная роль")

            total_lines += lines_
            total_tokens += tokens_
            total_comments += comments_

            lines_str = f"{lines_:,}".replace(",", " ")
            tokens_str = f"{tokens_:,}".replace(",", " ")
            comments_str = f"{comments_:,}".replace(",", " ")

            report_lines.append(
                f"📄 {full_path} — {role_} | "
                f"🔢 {lines_str} строк | 💬 {comments_str} комм. | 🏷 {tokens_str} токенов"
            )

    # Итог по репо
    lines_str = f"{total_lines:,}".replace(",", " ")
    tokens_str = f"{total_tokens:,}".replace(",", " ")
    comments_str = f"{total_comments:,}".replace(",", " ")

    report_lines.append("=" * 100)
    report_lines.append(f"📊 Итог по репозиторию: {repository_name}")
    report_lines.append(f"📜 Всего строк кода: {lines_str}")
    report_lines.append(f"💬 Всего комментариев: {comments_str}")
    report_lines.append(f"🏷 Всего токенов: {tokens_str}")
    report_lines.append("=" * 100)

    return "\n".join(report_lines)

def format_project_summary(project_name, repositories_reports):
    """
    Форматирует сводный отчёт по проекту.
    """
    # Суммы
    total_files = sum(len(repo.get("files", [])) for repo in repositories_reports if isinstance(repo, dict))
    total_lines = sum(
        sum(file.get("lines", 0) for file in repo.get("files", []))
        for repo in repositories_reports if isinstance(repo, dict)
    )
    total_comments = sum(
        sum(file.get("comments", 0) for file in repo.get("files", []))
        for repo in repositories_reports if isinstance(repo, dict)
    )
    total_tokens = sum(
        sum(file.get("tokens", 0) for file in repo.get("files", []))
        for repo in repositories_reports if isinstance(repo, dict)
    )

    # Форматируем с пробелами
    total_files_str = f"{total_files:,}".replace(",", " ")
    total_lines_str = f"{total_lines:,}".replace(",", " ")
    total_comments_str = f"{total_comments:,}".replace(",", " ")
    total_tokens_str = f"{total_tokens:,}".replace(",", " ")

    report_lines = [
        f"📊 Сводный отчёт по проекту: {project_name}",
        "=" * 100,
        f"📂 Количество репозиториев: {len(repositories_reports)}",
        f"📄 Всего файлов: {total_files_str}",
        f"📜 Всего строк кода: {total_lines_str}",
        f"💬 Всего комментариев: {total_comments_str}",
        f"🏷 Всего токенов: {total_tokens_str}",
        "=" * 100,
        "\n📂 Анализированные репозитории:\n"
    ]

    for idx, repo in enumerate(repositories_reports, start=1):
        if not isinstance(repo, dict):
            continue
        repo_tokens = sum(file.get("tokens", 0) for file in repo.get("files", []))
        repo_lines = sum(file.get("lines", 0) for file in repo.get("files", []))

        repo_tokens_str = f"{repo_tokens:,}".replace(",", " ")
        repo_lines_str = f"{repo_lines:,}".replace(",", " ")

        repo_name = repo.get("repository", "Неизвестный репозиторий")
        report_lines.append(
            f"🔹 {idx}. {repo_name} — {repo_tokens_str} токенов, {repo_lines_str} строк"
        )

    report_lines.append("\n⚫ Итог:")
    report_lines.append(f"📌 Общее количество токенов в проекте: {total_tokens_str}")
    report_lines.append("=" * 100)

    return "\n".join(report_lines)

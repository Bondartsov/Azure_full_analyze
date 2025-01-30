# core/reports/report_formatter.py

import json  # Для отладки

def format_repository_report(project_name, repository_name, files_data):
    """
    Форматирует отчёт для отдельного репозитория.
    :param project_name: Название проекта.
    :param repository_name: Название репозитория.
    :param files_data: Данные о файлах в репозитории.
    :return: Отформатированный текст отчёта.
    """
    report_lines = [
        f"📂 Отчёт о быстром анализе репозитория: {repository_name}",
        "=" * 100,
        f"📌 Проект: {project_name}",
        f"📌 Репозиторий: {repository_name}",
        "=" * 100,
        "\n📊 Структура файлов:\n"
    ]

    if not files_data:
        report_lines.append("⚠ Внимание: В репозитории нет данных для анализа.")
        return "\n".join(report_lines)

    folder_structure = {}
    for file in files_data:
        folder, filename = file["path"].rsplit("/", 1) if "/" in file["path"] else ("Корневая директория", file["path"])
        folder_structure.setdefault(folder, []).append((file["path"], filename, file))  # Сохраняем путь

    total_lines = 0
    total_tokens = 0

    for folder, files in sorted(folder_structure.items()):
        report_lines.append(f"\n📂 {folder}")
        report_lines.append("-" * 80)
        for full_path, filename, file in sorted(files, key=lambda x: x[0]):
            total_lines += file.get('lines', 0)
            total_tokens += file.get('tokens', 0)
            report_lines.append(
                f"📄 {full_path} — {file.get('role', 'Неизвестная роль')} | "
                f"🔢 {file.get('lines', 0)} строк | 💬 {file.get('comments', 0)} комм. | 🏷 {file.get('tokens', 0)} токенов"
            )

    report_lines.append("=" * 100)
    report_lines.append(f"📊 Итог по репозиторию: {repository_name}")
    report_lines.append(f"📜 Всего строк кода: {total_lines}")
    report_lines.append(f"🏷 Всего токенов: {total_tokens}")
    report_lines.append("=" * 100)

    # Логирование данных для отладки
    print(f"\n[DEBUG] Файлы, переданные в форматирование для {repository_name}:")
    print(json.dumps(files_data, indent=4, ensure_ascii=False))

    return "\n".join(report_lines)


def format_project_summary(project_name, repositories_reports):
    """
    Форматирует сводный отчёт по проекту.
    :param project_name: Название проекта.
    :param repositories_reports: Данные по всем репозиториям.
    :return: Отформатированный текст отчёта.
    """
    total_files = sum(len(repo.get("files", [])) for repo in repositories_reports if isinstance(repo, dict))
    total_lines = sum(sum(file.get("lines", 0) for file in repo.get("files", [])) for repo in repositories_reports if isinstance(repo, dict))
    total_comments = sum(sum(file.get("comments", 0) for file in repo.get("files", [])) for repo in repositories_reports if isinstance(repo, dict))
    total_tokens = sum(sum(file.get("tokens", 0) for file in repo.get("files", [])) for repo in repositories_reports if isinstance(repo, dict))

    report_lines = [
        f"📊 Сводный отчёт по проекту: {project_name}",
        "=" * 100,
        f"📂 Количество репозиториев: {len(repositories_reports)}",
        f"📄 Всего файлов: {total_files}",
        f"📜 Всего строк кода: {total_lines}",
        f"💬 Всего комментариев: {total_comments}",
        f"🏷 Всего токенов: {total_tokens}",
        "=" * 100,
        "\n📂 Анализированные репозитории:\n"
    ]

    for idx, repo in enumerate(repositories_reports, start=1):
        repo_tokens = sum(file.get("tokens", 0) for file in repo.get("files", []))
        repo_lines = sum(file.get("lines", 0) for file in repo.get("files", []))
        report_lines.append(f"🔹 {idx}. {repo['repository']} — {repo_tokens} токенов, {repo_lines} строк")

    report_lines.append("\n⚫ Итог:")
    report_lines.append(f"📌 Общее количество токенов в проекте: {total_tokens}")
    report_lines.append("=" * 100)

    return "\n".join(report_lines)

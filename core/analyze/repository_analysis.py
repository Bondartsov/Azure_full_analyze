# core/analyze/repository_analysis.py
import os
from core.reports.generate import generate_report
from core.utils.cache import load_repo_data_from_cache, save_repo_data_to_cache
from core.utils.token_counter import count_tokens_in_repo
from core.logging.logger import log
from core.ai.report_generator import (
    generate_ai_report,
    generate_deep_report_for_repo,
    get_deep_reports_for_repo
)

def analyze_repository(project_name, repository, repo_changed, analysis_mode="fast"):
    """
    Анализ одного репозитория.
      - Если analysis_mode == "fast" и repo_changed == False, пытаемся взять кэш.
      - Если analysis_mode == "deep" или кэш отсутствует, выполняем полный анализ.
    Возвращает словарь с результатами анализа.
    """
    repository_name = repository.name

    if analysis_mode == "fast" and not repo_changed:
        cached_data = load_repo_data_from_cache(project_name, repository_name)
        if cached_data:
            total_tokens = cached_data.get("total_tokens", 0)
            files_data = cached_data.get("files", [])
            report_path = generate_report(project_name, repository_name, files_data)
            if report_path:
                log(f"📄 Отчёт анализа {repository_name} сохранён (из кэша): {report_path}")
                return {
                    "repository": repository_name,
                    "tokens": total_tokens,
                    "cached": True,
                    "files": files_data,
                    "report_path": report_path
                }
            else:
                log(f"❌ Ошибка при генерации отчёта из кэша для {repository_name}!", level="ERROR")
                return None

    return analyze_repository_from_scratch(project_name, repository.name, analysis_mode)

def analyze_repository_from_scratch(project_name, repository_name, analysis_mode="fast"):
    """
    Считает токены заново, генерирует отчёт и (при глубоком анализе) ИИ‑отчёты,
    затем сохраняет данные в кэше (при быстром анализе).
    Возвращает словарь с результатами анализа.
    """
    token_result = count_tokens_in_repo(project_name, repository_name)
    if not token_result or not isinstance(token_result, tuple) or len(token_result) != 2:
        log("❌ Неверный формат данных от count_tokens_in_repo!", level="ERROR")
        return None

    files_data, total_tokens = token_result

    if analysis_mode == "fast":
        report_path = generate_report(project_name, repository_name, files_data)
    elif analysis_mode == "deep":
        # Выполнение глубокого анализа: генерируется агрегированный ИИ‑отчёт
        report_path = generate_deep_report_for_repo(project_name, repository_name, files_data)
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                aggregated_content = f.read()
            print("Aggregated Deep Analysis Report:\n", aggregated_content, flush=True)
        except Exception as e:
            log(f"❌ Ошибка при чтении агрегированного отчёта: {e}", level="ERROR")
    else:
        report_path = generate_report(project_name, repository_name, files_data)

    if not report_path:
        log(f"❌ Ошибка при генерации отчёта для {repository_name}", level="ERROR")
        return None

    if analysis_mode == "fast":
        from core.utils.cache import save_repo_data_to_cache
        save_repo_data_to_cache(project_name, repository_name, total_tokens, files_data)
    
    log(f"📄 Отчёт анализа {repository_name} сохранён: {report_path}")

    result = {
        "repository": repository_name,
        "tokens": total_tokens,
        "cached": False,  # Анализ с нуля – кэш не используется
        "files": files_data,
        "report_path": report_path
    }

    if analysis_mode == "deep":
        deep_reports = get_deep_reports_for_repo(project_name, repository_name, files_data)
        result["ai_reports"] = deep_reports

    return result
def generate_deep_report_for_repo(project_name, repository_name, files_data):
    """
    Для глубокого анализа генерирует ИИ‑отчёты для каждого файла репозитория.
    Собирает пути созданных отчётов и формирует агрегированный сводный отчёт.
    После создания агрегированного отчёта его содержимое выводится в консоль.
    Возвращает абсолютный путь к агрегированному отчёту.
    """
    # Локальный импорт, чтобы избежать циклического импорта
    from core.ai.report_generator import generate_ai_report
    deep_report_paths = []
    for file_info in files_data:
        # Ожидается, что file_info содержит "file_name", "folder" и "content"
        file_name = file_info.get("file_name")
        folder = file_info.get("folder", "root")
        file_content = file_info.get("content")
        if not file_content:
            continue
        try:
            report_path = generate_ai_report(project_name, repository_name, folder, file_name, file_content)
            deep_report_paths.append(report_path)
        except Exception as e:
            log(f"❌ Ошибка генерации ИИ‑отчёта для файла {file_name}: {e}", level="ERROR")
    
    aggregated_dir = os.path.join("ai_reports", project_name, repository_name)
    os.makedirs(aggregated_dir, exist_ok=True)
    aggregated_report_path = os.path.join(aggregated_dir, "aggregated_deep_report.txt")
    try:
        with open(aggregated_report_path, "w", encoding="utf-8") as f:
            header = f"Агрегированный ИИ‑анализ для репозитория {repository_name}\n\n"
            f.write(header)
            for path in deep_report_paths:
                f.write(f"{path}\n")
        # Вывод агрегированного отчёта в консоль
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
    from core.ai.report_generator import generate_ai_report
    deep_reports = []
    for file_info in files_data:
        file_name = file_info.get("file_name")
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

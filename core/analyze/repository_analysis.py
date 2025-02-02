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
    Анализ репозитория.
      - Если analysis_mode == "fast", запускается быстрый анализ.
      - Если analysis_mode == "deep", сначала выполняется быстрый анализ, а затем глубокий.
    """
    repository_name = repository.name

    print(f"DEBUG: Анализ {repository_name}, режим: {analysis_mode}")
    log(f"🔍 Анализ {repository_name}, режим: {analysis_mode}")

    fast_results = analyze_repository_fast(project_name, repository_name, repo_changed)
    
    if not fast_results:
        return None

    if analysis_mode == "deep":
        print(f"DEBUG: ВЫЗЫВАЕМ ГЛУБОКИЙ АНАЛИЗ ДЛЯ {repository_name}")
        log(f"🧠 Запуск глубокого ИИ-анализа для {repository_name}")
        print("DEBUG: Вызов get_deep_reports_for_repo")
        deep_reports = analyze_repository_deep(project_name, repository_name, fast_results)

        fast_results["ai_reports"] = deep_reports

    return fast_results

def analyze_repository_fast(project_name, repository_name, repo_changed):
    """Быстрый анализ репозитория: подсчёт токенов, обработка файлов, отчёт."""
    if not repo_changed:
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
    files_data, total_tokens = count_tokens_in_repo(project_name, repository_name)
    report_path = generate_report(project_name, repository_name, files_data)
    save_repo_data_to_cache(project_name, repository_name, total_tokens, files_data)
    log(f"📄 Отчёт анализа {repository_name} сохранён: {report_path}")
    
    return {
        "repository": repository_name,
        "tokens": total_tokens,
        "cached": False,
        "files": files_data,
        "report_path": report_path
    }
def analyze_repository_deep(project_name, repository_name, fast_results):
    """Глубокий ИИ-анализ на основе уже полученных данных."""
    
    print(f"DEBUG: Глубокий анализ активирован для {repository_name}")
    log(f"🧠 Выполняется глубокий ИИ-анализ для {repository_name}")
    
    if not isinstance(fast_results, dict):
        raise ValueError("fast_results должен быть словарем, а не списком")
    
    files_data = fast_results.get("files", [])
    print(f"DEBUG: Файлы для глубокого анализа: {len(files_data)} шт.")
    log(f"🔎 Количество файлов для глубокого анализа: {len(files_data)}")
    deep_reports = get_deep_reports_for_repo(project_name, repository_name, files_data)
    print(f"DEBUG: Найдено {len(deep_reports)} ИИ-отчётов")
    log(f"📝 Найдено {len(deep_reports)} ИИ-отчётов для {repository_name}")
    return deep_reports
def generate_deep_report_for_repo(project_name, repository_name, files_data):
    """
    Генерирует агрегированный ИИ-отчёт по всем файлам репозитория.
    """
    deep_report_paths = []
    
    for file_info in files_data:
        file_name = file_info.get("file_name")
        folder = file_info.get("folder", "root")
        file_content = file_info.get("content")
        if not file_content:
            continue
        try:
            report_path = generate_ai_report(project_name, repository_name, folder, file_name, file_content)
            deep_report_paths.append(report_path)
        except Exception as e:
            log(f"❌ Ошибка генерации ИИ-отчёта для файла {file_name}: {e}", level="ERROR")
    
    aggregated_dir = os.path.join("ai_reports", project_name, repository_name)
    os.makedirs(aggregated_dir, exist_ok=True)
    aggregated_report_path = os.path.join(aggregated_dir, "aggregated_deep_report.txt")
    
    try:
        with open(aggregated_report_path, "w", encoding="utf-8") as f:
            header = f"Агрегированный ИИ-анализ для репозитория {repository_name}\n\n"
            f.write(header)
            for path in deep_report_paths:
                f.write(f"{path}\n")
        log(f"✅ Агрегированный ИИ-отчёт сохранён: {aggregated_report_path}")
    except Exception as e:
        log(f"❌ Ошибка при сохранении агрегированного ИИ-отчёта: {e}", level="ERROR")

    return aggregated_report_path

# repository_analysis.py

def get_deep_reports_for_repo(project_name, repository_name, files_data):
    """
    Возвращает список абсолютных путей к индивидуальным ИИ-отчётам для каждого файла.
    """
    log(f"🔍 Запуск функции get_deep_reports_for_repo для репозитория: {repository_name}")
    print(f"🔍 Запуск функции get_deep_reports_for_repo для репозитория: {repository_name}")

    deep_reports = []
    for file_info in files_data:
        file_name = file_info.get("file_name") or file_info.get("path")
        folder = file_info.get("folder", "root")
        file_content = file_info.get("content")

        log(f"📂 Обработка файла: {file_name}")
        print(f"📂 Обработка файла: {file_name}")

        if not file_content:
            log(f"⚠️ Пропущен пустой файл: {file_name}")
            print(f"⚠️ Пропущен пустой файл: {file_name}")
            continue

        # Добавляем логирование содержимого файла для отладки
        log(f"📝 Содержимое файла {file_name}: {len(file_content)} символов")
        print(f"📝 Содержимое файла {file_name}: {len(file_content)} символов")

        try:
            report_path = generate_ai_report(project_name, repository_name, folder, file_name, file_content)
            if report_path:
                deep_reports.append(os.path.abspath(report_path))
                log(f"✅ Отчёт для файла {file_name} успешно создан: {report_path}")
                print(f"✅ Отчёт для файла {file_name} успешно создан: {report_path}")
            else:
                log(f"❌ Не удалось создать отчёт для файла {file_name}!", level="ERROR")
                print(f"❌ Не удалось создать отчёт для файла {file_name}!")
        except Exception as e:
            log(f"❌ Ошибка генерации ИИ‑отчёта для файла {file_name}: {e}", level="ERROR")
            print(f"❌ Ошибка генерации ИИ‑отчёта для файла {file_name}: {e}")

    log(f"📝 Завершение функции get_deep_reports_for_repo, создано {len(deep_reports)} отчётов.")
    print(f"📝 Завершение функции get_deep_reports_for_repo, создано {len(deep_reports)} отчётов.")
    return deep_reports
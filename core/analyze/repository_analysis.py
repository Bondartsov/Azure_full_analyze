from core.reports.generate import generate_report
from core.utils.cache import load_repo_data_from_cache, save_repo_data_to_cache
from core.utils.token_counter import count_tokens_in_repo
from core.logging.logger import log

def analyze_repository(project_name, repository, repo_changed):
    """
    Анализ одного репозитория:
      - Если repo_changed=False, пытаемся взять кэш, генерируем отчёт и выходим.
      - Иначе считаем заново, генерируем отчёт, записываем в кэш.
    Возвращает словарь:
       {
         "repository": <str>,
         "tokens": <int>,
         "cached": <bool>,
         "files": <list[...dict...]>,
         "report_path": <str>  # или None
       }
    """
    repository_name = repository.name

    if not repo_changed:
        # -> берём кэш
        cached_data = load_repo_data_from_cache(project_name, repository_name)
        if not cached_data:
            # Может случиться, что is_repo_changed=False, но кэша всё же нет.
            # В таком случае всё равно пересчитываем.
            return analyze_repository_from_scratch(project_name, repository_name)

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

    # Если repo_changed=True или кэш пуст — делаем полный анализ
    return analyze_repository_from_scratch(project_name, repository_name)

def analyze_repository_from_scratch(project_name, repository_name):
    """
    Считает токены заново, генерирует отчёт и сохраняет данные в кэш.
    """
    token_result = count_tokens_in_repo(project_name, repository_name)
    if not token_result or not isinstance(token_result, tuple) or len(token_result) != 2:
        log("❌ Неверный формат данных от count_tokens_in_repo!", level="ERROR")
        return None

    files_data, total_tokens = token_result

    report_path = generate_report(project_name, repository_name, files_data)
    if not report_path:
        log(f"❌ Ошибка при генерации отчёта для {repository_name}", level="ERROR")
        return None

    # Сохраняем в кэш
    save_repo_data_to_cache(project_name, repository_name, total_tokens, files_data)
    log(f"📄 Отчёт анализа {repository_name} сохранён: {report_path}")

    return {
        "repository": repository_name,
        "tokens": total_tokens,
        "cached": False,
        "files": files_data,
        "report_path": report_path
    }

import json
from tqdm import tqdm

from core.azure.repo_commits import get_all_commits, get_last_commit
from core.analyze.commit_analysis import analyze_commits
from core.reports.generate import generate_report
from core.utils.cache import is_repo_changed, save_repo_data_to_cache, load_repo_data_from_cache
from core.utils.token_counter import count_tokens_in_repo
from core.logging.logger import log


def analyze_repository(project_name, repository, progress_bar=None):
    """
    Функция анализа одного репозитория:
    1. Проверяем, есть ли изменения (is_repo_changed).
    2. Если нет изменений и данные есть в кэше, берём их и генерируем отчёт.
    3. Если репозиторий изменён или в кэше нет данных, заново считаем токены,
       получаем коммиты, анализируем их и генерируем отчёт.

    :param project_name: Название проекта (str).
    :param repository: Объект репозитория (должен иметь атрибут 'name').
    :param progress_bar: Опционально, объект tqdm для отображения прогресса.
    :return: Словарь с итогами анализа или None при ошибке.
    """
    repository_name = repository.name

    if progress_bar:
        progress_bar.set_description(f"🔍 Анализ: {repository_name}")

    log(f"\n📂 Начало анализа репозитория: {repository_name}")
    print(f"\n📂 Начало анализа репозитория: {repository_name}", flush=True)

    # 1. Получаем последний коммит и проверяем, есть ли изменения
    latest_commit = get_last_commit(project_name, repository_name)
    repo_changed = is_repo_changed(project_name, repository_name, latest_commit)

    if not repo_changed:
        # Пробуем загрузить данные из кэша
        cached_data = load_repo_data_from_cache(project_name, repository_name)
        if cached_data:
            # Предполагаем, что в кэше храним (total_tokens, commit_count, files_data, analysis)
            total_tokens, commit_count, files_data, cached_analysis = cached_data

            # Если старый кэш содержал данные в виде dict {"filename.py": 123, ...},
            # то превращаем в список словарей [{"path": ..., "tokens": ...}]
            if isinstance(files_data, dict):
                log(f"⚠ Старый формат files_data (dict). Преобразуем в список словарей...", level="WARNING")
                files_data = [{"path": k, "tokens": v} for k, v in files_data.items()]

            # Если files_data было списком чисел или чем-то ещё — проверяем
            if not isinstance(files_data, list):
                log(f"❌ Фатальная ошибка: files_data должен быть списком, а получен {type(files_data)}", level="ERROR")
                return None

            log(f"✅ Используем закэшированные данные для {repository_name}: {total_tokens} токенов, {commit_count} коммитов")
            print(f"✅ Используем закэшированные данные для {repository_name}: {total_tokens} токенов, {commit_count} коммитов", flush=True)

            # Генерация отчёта из кэша
            report_path = generate_report(project_name, repository_name, files_data)
            if report_path:
                log(f"📄 Отчёт из кэша сохранён: {report_path}")
                print(f"📄 Отчёт из кэша сохранён: {report_path}", flush=True)

                if progress_bar:
                    progress_bar.update(1)

                return {
                    "repository": repository_name,
                    "tokens": total_tokens,
                    "commits": commit_count,
                    "analysis": cached_analysis,
                    "cached": True,
                    "files": files_data,
                }
            else:
                # Если отчёт не сгенерировался
                log("❌ Ошибка при генерации отчёта из кэша!", level="ERROR")
                return None

    # 2. Если изменений нет, но кэша нет, или репозиторий изменён — пересчитываем
    log(f"📊 Подсчёт токенов в {repository_name}...")
    print(f"📊 Подсчёт токенов в {repository_name}...", flush=True)

    # count_tokens_in_repo должно возвращать кортеж (files_list, total_tokens)
    result = count_tokens_in_repo(project_name, repository_name)
    if not result or not isinstance(result, tuple) or len(result) != 2:
        log(f"❌ Неверный формат данных от count_tokens_in_repo!", level="ERROR")
        return None

    files_data, total_tokens = result  # files_data → list[{"path": str, "tokens": int}]

    log(f"✅ Подсчёт токенов завершён: {total_tokens} токенов")
    print(f"✅ Подсчёт токенов завершён: {total_tokens} токенов", flush=True)

    # Дополнительная защита: вдруг кто-то вернёт не список
    if not isinstance(files_data, list):
        log(f"❌ Фатальная ошибка: files_data должен быть списком, а получен {type(files_data)}", level="ERROR")
        return None

    # 3. Получаем коммиты
    log(f"🔄 Получение коммитов для {repository_name}...")
    print(f"🔄 Получение коммитов для {repository_name}...", flush=True)
    commits = get_all_commits(project_name, repository_name)
    if commits is None:
        log(f"⚠ Ошибка при получении коммитов для {repository_name}", level="ERROR")
        print(f"⚠ Ошибка при получении коммитов для {repository_name}", flush=True)
        if progress_bar:
            progress_bar.update(1)
        return None

    log(f"📌 Найдено {len(commits)} коммитов")
    print(f"📌 Найдено {len(commits)} коммитов", flush=True)

    # 4. Анализ коммитов
    analysis = analyze_commits(commits) if commits else {"total_commits": 0, "top_authors": []}
    log(f"📊 Анализ завершён:\n{json.dumps(analysis, indent=4, ensure_ascii=False)}")
    print(f"📊 Анализ завершён:\n{json.dumps(analysis, indent=4, ensure_ascii=False)}", flush=True)

    # 5. Генерация отчёта
    log("📄 Генерация отчёта...")
    print("📄 Генерация отчёта...", flush=True)
    report_path = generate_report(project_name, repository_name, files_data)

    if report_path:
        log(f"✅ Отчёт сохранён: {report_path}")
        print(f"✅ Отчёт сохранён: {report_path}", flush=True)

        # Сохраняем в кэш новые данные + анализ
        save_repo_data_to_cache(project_name, repository_name, total_tokens, len(commits), files_data, analysis)
        if progress_bar:
            progress_bar.update(1)

        print(f"✅ Анализ завершён для {repository_name}", flush=True)

        return {
            "repository": repository_name,
            "tokens": total_tokens,
            "commits": len(commits),
            "analysis": analysis,
            "cached": False,
            "files": files_data,
        }
    else:
        log("❌ Ошибка при генерации отчёта!", level="ERROR")
        print("❌ Ошибка при генерации отчёта!", flush=True)
        if progress_bar:
            progress_bar.update(1)
        return None

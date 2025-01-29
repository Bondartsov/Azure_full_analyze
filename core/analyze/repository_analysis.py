from core.azure.repo_commits import get_all_commits, get_last_commit
from core.analyze.commit_analysis import analyze_commits
from core.reports.generate import generate_report
from core.utils.cache import is_repo_changed, load_repo_data_from_cache, save_repo_data_to_cache
from core.logging.logger import log
from core.utils.token_counter import count_tokens_in_repo
from core.utils.common import format_number
from tqdm import tqdm


def analyze_repository(project_name, repository, progress_bar=None):
    """Функция анализа одного репозитория"""
    repository_name = repository.name

    # 🔹 Разделитель перед каждым репозиторием (ставится один раз!)
    print("\n" + "=" * 80 + "\n", flush=True)

    log(f"📂 Начало анализа репозитория: {repository_name}")
    print(f"📂 Начало анализа репозитория: {repository_name}", flush=True)

    latest_commit = get_last_commit(project_name, repository_name)
    repo_changed = is_repo_changed(project_name, repository_name, latest_commit)

    if not repo_changed:
        cached_data = load_repo_data_from_cache(project_name, repository_name)
        if cached_data:
            total_tokens, commit_count = cached_data
            if total_tokens > 0:
                log(f"✅ Используем закэшированные данные для {repository_name}: {format_number(total_tokens)} токенов, {format_number(commit_count)} коммитов")
                print(f"✅ Используем закэшированные данные для {repository_name}: {format_number(total_tokens)} токенов, {format_number(commit_count)} коммитов", flush=True)
                
                report_path = generate_report(project_name, repository_name, total_tokens, [], {"total_commits": commit_count, "top_authors": []})
                log(f"📄 Отчёт из кэша сохранён: {report_path}")
                print(f"📄 Отчёт из кэша сохранён: {report_path}", flush=True)

                if progress_bar:
                    progress_bar.update(1)

                # 🔹 Добавляем разделитель в конце анализа репозитория
                print("\n" + "=" * 80, flush=True)
                return {"repository": repository_name, "tokens": total_tokens, "commits": commit_count, "cached": True}
    
    # 🔹 Если кэша нет или он пустой → анализируем
    log(f"📊 Подсчёт токенов в {repository_name}...")
    print(f"📊 Подсчёт токенов в {repository_name}...", flush=True)

    token_data, total_tokens = count_tokens_in_repo(project_name, repository_name)
    log(f"✅ Подсчёт токенов завершён: {format_number(total_tokens)} токенов")
    print(f"✅ Подсчёт токенов завершён: {format_number(total_tokens)} токенов", flush=True)

    commits = get_all_commits(project_name, repository_name)

    if commits is None:
        log(f"⚠ Ошибка при получении коммитов для {repository_name}", level="ERROR")
        print(f"⚠ Ошибка при получении коммитов для {repository_name}", flush=True)
        if progress_bar:
            progress_bar.update(1)
        return None

    log(f"📌 Найдено {format_number(len(commits))} коммитов")
    print(f"📌 Найдено {format_number(len(commits))} коммитов", flush=True)

    analysis = analyze_commits(commits) if commits else {"total_commits": 0, "top_authors": []}
    log(f"📊 Анализ завершён: {analysis}")
    print(f"📊 Анализ завершён: {analysis}", flush=True)

    report_path = generate_report(project_name, repository_name, total_tokens, commits, analysis)

    if report_path:
        log(f"✅ Отчёт сохранён: {report_path}")
        print(f"✅ Отчёт сохранён: {report_path}", flush=True)

        save_repo_data_to_cache(project_name, repository_name, total_tokens, len(commits))
        if progress_bar:
            progress_bar.update(1)

        print(f"✅ Анализ завершён для {repository_name}", flush=True)

        # 🔹 Добавляем разделитель в конце анализа репозитория
        print("\n" + "=" * 80, flush=True)
        return {"repository": repository_name, "tokens": total_tokens, "commits": len(commits), "cached": False}
    else:
        log("❌ Ошибка при генерации отчёта!", level="ERROR")
        print("❌ Ошибка при генерации отчёта!", flush=True)
        if progress_bar:
            progress_bar.update(1)
        return None

# core\analyze\commit_analisis.py
from collections import Counter
from core.logging.logger import log

def analyze_commits(commits):
    """
    Анализ списка коммитов.
    Возвращает количество коммитов и самых активных авторов.
    """
    if not commits:
        log("Коммиты отсутствуют. Анализ невозможен.", level="WARNING")
        return {"total_commits": 0, "top_authors": []}

    authors = [commit.author.name for commit in commits if commit.author]
    total_commits = len(commits)
    top_authors = Counter(authors).most_common(5)  # Топ-5 авторов

    log(f"Анализ коммитов завершён: всего {total_commits}, топ-5 авторов: {top_authors}")
    return {
        "total_commits": total_commits,
        "top_authors": top_authors
    }

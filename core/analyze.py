from collections import Counter

def analyze_commits(commits):
    """
    Анализ списка коммитов.
    Возвращает количество коммитов и самых активных авторов.
    """
    authors = [commit.author.name for commit in commits if commit.author]
    total_commits = len(commits)
    top_authors = Counter(authors).most_common(5)  # Топ-5 авторов
    return {
        "total_commits": total_commits,
        "top_authors": top_authors
    }
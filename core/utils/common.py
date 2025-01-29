from core.azure.projects import get_projects
from core.azure.repos import get_repositories
from core.logging.logger import log

def choose_from_list(options, prompt):
    """
    Выводит список опций и предлагает пользователю выбрать одну из них.
    Возвращает выбранную опцию.
    """
    print(f"\n{prompt}")
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")

    while True:
        try:
            choice = int(input("Введите номер: "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print("⚠ Неверный ввод. Попробуйте снова.")
        except ValueError:
            print("⚠ Введите число.")

def select_project():
    """
    Получает список проектов из Azure DevOps и предлагает пользователю выбрать один.
    Возвращает название выбранного проекта.
    """
    projects = get_projects()
    log(f"📌 Доступные проекты: {projects}")
    
    if not projects:
        log("⚠ Нет доступных проектов.", level="WARNING")
        return None

    project_name = choose_from_list(projects, "Выберите проект")
    log(f"✅ Выбран проект: {project_name}")
    
    return project_name


def select_repositories(project_name):
    """
    Получает список репозиториев для выбранного проекта и предлагает пользователю выбрать:
    - Анализировать все репозитории
    - Анализировать конкретный репозиторий
    
    Возвращает список репозиториев или один выбранный репозиторий.
    """
    repositories = get_repositories(project_name)
    log(f"📌 Найдено {len(repositories)} репозиториев.")

    if not repositories:
        log(f"⚠ Нет репозиториев в проекте {project_name}.", level="WARNING")
        return [], None  # Возвращаем пустой список

    options = ["📂 Анализировать все репозитории"] + [repo.name for repo in repositories]
    selected_option = choose_from_list(options, f"Выберите действие в проекте {project_name}")  # ✅ Добавлено имя проекта

    if selected_option == "📂 Анализировать все репозитории":
        return repositories, None  # Все репозитории
    else:
        repository = next((repo for repo in repositories if repo.name == selected_option), None)
        return None, repository  # Один репозиторий

def format_number(number):
    """Форматирует числа с пробелами (1000000 -> 1 000 000)"""
    return f"{number:,}".replace(",", " ")

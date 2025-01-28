# core/azure/projects.py
from core.azure.connection import connect_to_azure
from core.logging.logger import log

def get_projects():
    """
    Получает список проектов в Azure DevOps.
    """
    try:
        connection = connect_to_azure()
        core_client = connection.clients.get_core_client()
        projects = core_client.get_projects()
        log(f"Получено {len(projects)} проектов.")
        return [project.name for project in projects]
    except Exception as e:
        log(f"Ошибка при получении проектов: {str(e)}", level="ERROR")
        return []

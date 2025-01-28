# core/azure/projects.py
def get_projects(connection):
    try:
        core_client = connection.clients.get_core_client()
        projects = core_client.get_projects()
        return [project.name for project in projects]
    except Exception as e:
        print(f"Ошибка при получении проектов: {str(e)}")
        return []

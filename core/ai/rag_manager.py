import json
import os
from core.ai.rag_storage import search_rag

RAG_DB = "rag_data.json"

def store_in_rag(project_name, repository_name, folder_name, file_name, analysis):
    """
    Сохраняет анализ в RAG и возвращает True при успешном выполнении.
    """
    data = {
        "project": project_name,
        "repository": repository_name,
        "folder": folder_name,
        "file": file_name,
        "analysis": analysis
    }

    if os.path.exists(RAG_DB):
        with open(RAG_DB, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    existing_data.append(data)

    with open(RAG_DB, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)

    return True  # Возвращаем True после успешного сохранения

def query_rag(project_name, repository_name, folder_name, file_name, query):
    print(f"🔍 Querying RAG: project={project_name}, repo={repository_name}, folder={folder_name}, file={file_name}, query='{query}'")

    # Проверяем, есть ли данные
    results = search_rag(project_name, repository_name, folder_name, file_name, query)
    if not results:
        print("⚠️ Нет данных в RAG!")
        return "❌ Нет данных по запросу."

    return results[0]  # Гарантируем, что возвращаем строку

import os

# Папка для хранения RAG-данных
RAG_STORAGE_DIR = "rag_data"

def search_rag(project_name, repository_name, folder_name, file_name, query):
    file_path = os.path.join(RAG_STORAGE_DIR, project_name, repository_name, folder_name, f"{file_name}.txt")

    if not os.path.exists(file_path):
        print(f"⚠️ Файл {file_path} не найден в RAG!")
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    results = [line.strip() for line in lines if query.lower() in line.lower()]

    if not results:
        print(f"🔍 По запросу '{query}' ничего не найдено в {file_path}")

    return results if results else ["❌ Нет данных."]

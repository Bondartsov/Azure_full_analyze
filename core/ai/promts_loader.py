import os

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "promts")

def load_prompt(prompt_name):
    """
    Загружает текстовый промпт из папки core/ai/promts.

    :param prompt_name: Название файла промпта (без .txt)
    :return: Строка с текстом промпта
    """
    prompt_path = os.path.join(PROMPTS_DIR, f"{prompt_name}.txt")

    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"⚠ Промпт {prompt_name}.txt не найден в {PROMPTS_DIR}")

    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

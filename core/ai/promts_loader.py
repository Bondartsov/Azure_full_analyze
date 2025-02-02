import os
from core.logging.logger import log


PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "promts")

def load_prompt(prompt_name):
    """
    Загружает текстовый промпт из папки core/ai/promts.
    """
    prompt_path = os.path.join(PROMPTS_DIR, f"{prompt_name}.txt")

    if not os.path.exists(prompt_path):
        log(f"⚠ Промпт {prompt_name}.txt не найден в {PROMPTS_DIR}")
        raise FileNotFoundError(f"⚠ Промпт {prompt_name}.txt не найден в {PROMPTS_DIR}")

    with open(prompt_path, "r", encoding="utf-8") as f:
        content = f.read()
        log(f"📄 Промпт {prompt_name}.txt успешно загружен.")
        return content
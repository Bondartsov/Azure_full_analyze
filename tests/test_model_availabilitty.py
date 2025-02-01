# tests/test_model_availability.py

from openai import OpenAI  # Корректный импорт класса OpenAI
from openai._exceptions import OpenAIError
import os
from dotenv import load_dotenv

load_dotenv(r"D:\Projects\Azure_full_analyze\.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "o1-mini")

client = OpenAI(api_key=OPENAI_API_KEY)

def test_model_availability():
    try:
        models = client.models.list()
        model_ids = [model.id for model in models.data]
        assert OPENAI_MODEL in model_ids, f"Модель {OPENAI_MODEL} недоступна."
        print(f"✅ Модель {OPENAI_MODEL} доступна.")
    except OpenAIError as e:
        assert False, f"Ошибка при проверке доступности модели: {e}"

if __name__ == "__main__":
    test_model_availability()
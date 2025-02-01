# tests/test_model_list.py

from openai import OpenAI
from openai._exceptions import OpenAIError
import os
from dotenv import load_dotenv
from core.logging.logger import log

load_dotenv(r"D:\Projects\Azure_full_analyze\.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def test_model_list():
    try:
        models = client.models.list()
        model_ids = [model.id for model in models.data]
        print("Доступные модели:")
        for model_id in model_ids:
            print(model_id)
    except OpenAIError as e:
        print(f"❌ Ошибка при получении списка моделей: {e}")

if __name__ == "__main__":
    test_model_list()
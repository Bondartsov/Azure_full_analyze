# core/ai/code_advisor.py

from openai import OpenAI
from openai._exceptions import (
    OpenAIError,
    APIConnectionError,
    RateLimitError,
    APIStatusError
)
import os
from dotenv import load_dotenv
from core.logging.logger import log

# Загружаем переменные окружения из файла .env
load_dotenv(r"D:\Projects\Azure_full_analyze\.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "o3-mini")  # Убедитесь, что модель указана правильно

# Инициализируем клиент OpenAI
client = OpenAI(
    api_key=OPENAI_API_KEY
)

def query_openai(prompt):
    """
    Отправляет запрос к модели OpenAI и возвращает анализ.
    Параметры temperature и max_tokens удалены, так как модель "o3-mini" их не поддерживает.
    """
    if not OPENAI_API_KEY:
        log("⚠️ API-ключ OpenAI не установлен!", level="ERROR")
        raise ValueError("⚠️ API-ключ OpenAI не установлен!")

    print(f"🔍 Отправка запроса в OpenAI: {prompt[:50]}...")
    log(f"📝 Полный промпт: {prompt}")

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            timeout=30  # Тайм-аут для запроса
            # temperature и max_tokens удалены
        )

        # Логирование полного ответа для диагностики
        log(f"📡 Полный ответ от OpenAI: {response.model_dump()}")

        choices = response.choices  # Доступ к списку выборок
        if not choices:
            log("⚠️ Нет выбора в ответе от OpenAI.", level="WARNING")
            return ""

        message = choices[0].message  # Доступ к сообщению
        if not hasattr(message, 'content'):
            log("⚠️ Сообщение не содержит содержимого.", level="WARNING")
            return ""

        analysis = message.content.strip()
        if not analysis:
            log("⚠️ Получен пустой анализ от OpenAI.", level="WARNING")
        else:
            log("✅ Получен анализ от OpenAI.")

        return analysis

    except APIConnectionError as e:
        log(f"❌ Ошибка подключения к OpenAI: {e}", level="ERROR")
        return ""

    except RateLimitError as e:
        log(f"❌ Превышен лимит запросов к OpenAI: {e}", level="ERROR")
        return ""

    except APIStatusError as e:
        log(f"❌ API ошибка от OpenAI: Статус {e.status_code}, Сообщение: {e.message}", level="ERROR")
        return ""

    except OpenAIError as e:
        log(f"❌ Общая ошибка OpenAI: {e}", level="ERROR")
        return ""

    except Exception as e:
        log(f"❌ Неизвестная ошибка при запросе к OpenAI: {e}", level="ERROR")
        return ""
import openai
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-latest")

def query_openai(prompt):
    if not OPENAI_API_KEY:
        raise ValueError("⚠️ API-ключ OpenAI не установлен!")

    print(f"🔍 Отправка запроса в OpenAI: {prompt[:50]}...")

    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            api_key=OPENAI_API_KEY.encode("utf-8").decode("utf-8")  # Принудительно кодируем в UTF-8
        )

        return response["choices"][0]["message"]["content"]
    
    except UnicodeEncodeError as e:
        print(f"❌ Ошибка кодировки API-ключа: {e}")
        raise

    except Exception as e:
        print(f"❌ Ошибка запроса к OpenAI: {e}")
        raise

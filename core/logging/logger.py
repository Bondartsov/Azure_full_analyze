# core/logging/logger.py

import logging
import os
import sqlite3
from dotenv import load_dotenv

# Загрузка переменных окружения из .env
load_dotenv()

# Получение пути к базе данных логов из .env или использование дефолтного пути
DB_PATH = os.getenv("LOG_DB_PATH", os.path.join(os.path.dirname(__file__), "../../logs.db"))

class SQLiteHandler(logging.Handler):
    """
    Класс-обработчик логов, пишущий в SQLite.
    Создаёт таблицу logs (id, created, level, message).
    """
    
    def __init__(self, db_path=DB_PATH):
        super().__init__()
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Создаёт таблицу логов, если её нет."""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS logs(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created TEXT,
                    level TEXT,
                    message TEXT
                )
                """
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Ошибка при создании таблицы логов: {e}")

    def emit(self, record):
        """Записывает лог в SQLite."""
        try:
            msg = self.format(record)
            level = record.levelname
            created = (
                self.formatter.formatTime(record, "%Y-%m-%d %H:%M:%S")
                if self.formatter
                else record.created
            )

            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute(
                "INSERT INTO logs(created, level, message) VALUES (?, ?, ?)",
                (created, level, msg),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Ошибка при записи лога в SQLite: {e}")
            self.handleError(record)  # Логируем ошибку обработки

def setup_logging(level=logging.INFO):
    """
    Настройка логирования в SQLite и консоль.
    """
    logger = logging.getLogger()
    logger.setLevel(level)

    # Удаляем старые хендлеры
    while logger.handlers:
        logger.handlers.pop()

    # Формат логов
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    # Лог в SQLite
    sqlite_handler = SQLiteHandler(DB_PATH)
    sqlite_handler.setFormatter(formatter)
    logger.addHandler(sqlite_handler)

    # Лог в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Удалите или закомментируйте FileHandler, если не хотите логировать в файл
    '''
    # Лог в файл logs/app.log (ротация)
    logs_dir = os.path.join(os.path.dirname(__file__), "../../logs")
    os.makedirs(logs_dir, exist_ok=True)  # Создаём папку для логов, если нет
    file_handler = logging.FileHandler(os.path.join(logs_dir, "app.log"), encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    '''

    logging.info("✅ Логирование инициализировано (SQLite + консоль).")

def log(message, level=logging.INFO):
    """
    Универсальный логгер.
    """
    if level == logging.DEBUG:
        logging.debug(message)
    elif level == logging.WARNING:
        logging.warning(message)
    elif level == logging.ERROR:
        logging.error(message)
    else:
        logging.info(message)

# ✅ Инициализация логов при импортировании модуля
setup_logging()

# Отключаем ненужные логи о версии API
class CustomFilter(logging.Filter):
    def filter(self, record):
        return "Negotiated api version" not in record.getMessage()

logger = logging.getLogger()
for handler in logger.handlers:
    handler.addFilter(CustomFilter())
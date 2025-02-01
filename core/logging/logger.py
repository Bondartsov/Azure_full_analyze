import logging
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), '../../logs.db')

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
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created TEXT,
            level TEXT,
            message TEXT
        )
        """)
        conn.commit()
        conn.close()

    def emit(self, record):
        """
        Записывает лог в SQLite.
        """
        try:
            msg = self.format(record)
            level = record.levelname
            # ✅ Исправление: Берём формат времени из форматтера
            if self.formatter:
                created = self.formatter.formatTime(record, "%Y-%m-%d %H:%M:%S")
            else:
                created = record.created  # Если форматтер не задан, берём raw timestamp

            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("INSERT INTO logs(created, level, message) VALUES (?, ?, ?)", (created, level, msg))
            conn.commit()
            conn.close()
        except Exception as e:
            self.handleError(record)  # Логируем ошибку обработки

def setup_logging(level=logging.INFO):
    """
    Настройка логирования в SQLite.
    """
    logger = logging.getLogger()
    logger.setLevel(level)

    # Удаляем старые хендлеры, чтобы не писать в файл
    while logger.handlers:
        logger.handlers.pop()

    # Создаём новый SQLite-хендлер
    sqlite_handler = SQLiteHandler(DB_PATH)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
    sqlite_handler.setFormatter(formatter)  # ✅ Устанавливаем форматтер с временем
    logger.addHandler(sqlite_handler)

    logging.info("Логирование инициализировано (SQLite).")

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

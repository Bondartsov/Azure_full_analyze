import logging
import os

def setup_logging(level=logging.INFO):
    """
    Настройка логирования.
    """
    log_file = os.path.join(os.path.dirname(__file__), '../../app.log')
    logging.basicConfig(
        filename=log_file,
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("Логирование инициализировано.")

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

# Инициализация логов при импортировании модуля
setup_logging()

import logging
import os

def setup_logging():
    logging.basicConfig(
        filename=os.path.join(os.path.dirname(__file__), '../app.log'),
        level=logging.INFO,
        format='%(asctime)s - %(message)s'
    )

def log(message):
    logging.info(message)
    print(f"[LOG] {message}")

setup_logging()
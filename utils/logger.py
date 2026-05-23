import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            RotatingFileHandler(
                "logs/bot.log",
                maxBytes=5 * 1024 * 1024,
                backupCount=3,
                encoding="utf-8"
            ),
            logging.StreamHandler()
        ]
    )
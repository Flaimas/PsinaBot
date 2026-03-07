import os
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из .env

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [123456789]  # ID администраторов

MARZBAN_URL = os.getenv("MARZBAN_URL") #url site
MARZBAN_USERNAME = os.getenv("MARZBAN_USERNAME")
MARZBAN_PASSWORD = os.getenv("MARZBAN_PASSWORD")
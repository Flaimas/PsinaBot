import os
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из .env

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
SUPPORT_URL = os.getenv("SUPPORT_URL")

MARZBAN_URL = os.getenv("MARZBAN_URL") #url site
MARZBAN_USERNAME = os.getenv("MARZBAN_USERNAME")
MARZBAN_PASSWORD = os.getenv("MARZBAN_PASSWORD")

PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN")
SECRET_KEY = os.getenv("SECRET_KEY")
ACCOUNT_ID = os.getenv("ACCOUNT_ID")

DB_PATH = 'orders.db'
PROXY_URL = 'http://127.0.0.1:10808'

UVICORN_IP = '127.0.0.1' #данные для webhook
UVICORN_PORT = 8001

MANUAL_PAYMENT=False #РУЧНАЯ ОПЛАТА
import os
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из .env

BOT_TOKEN = os.getenv("BOT_TOKEN")

admin_row = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(admin_id) for admin_id in admin_row.split(',') if admin_id]

SUPPORT_URL = os.getenv("SUPPORT_URL")

MARZBAN_URL = os.getenv("MARZBAN_URL") #url site
MARZBAN_USERNAME = os.getenv("MARZBAN_USERNAME")
MARZBAN_PASSWORD = os.getenv("MARZBAN_PASSWORD")

PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN")
SECRET_KEY = os.getenv("SECRET_KEY")
ACCOUNT_ID = os.getenv("ACCOUNT_ID")

DB_PATH = os.getenv("DB_PATH")
PROXY_URL = os.getenv("PROXY_URL")

UVICORN_IP = os.getenv('UVICORN_IP') #данные для webhook
UVICORN_PORT = int(os.getenv('UVICORN_PORT'))

SSL_CER = os.getenv("SSL_CER")
SSL_KEY = os.getenv("SSL_KEY")

REFERRAL_REWARD_RATIO = 0.1 #процент награды, начисляющийся реферерру
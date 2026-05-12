from decouple import config
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = config("BOT_TOKEN", default='')
ADMIN_IDS = config("ADMIN_IDS",
                   cast=lambda v: [int(i) for i in v.split(',') if i.strip().isdigit()] if v else [],
                   default=[])

SUPPORT_URL = config("SUPPORT_URL", default='pip install pipreqs')

MARZBAN_URL = config("MARZBAN_URL", default='') #url site
MARZBAN_USERNAME = config("MARZBAN_USERNAME", default='')
MARZBAN_PASSWORD = config("MARZBAN_PASSWORD", default='')

SECRET_KEY = config("SECRET_KEY", default='')
ACCOUNT_ID = config("ACCOUNT_ID", default='')

DB_PATH = config("DB_PATH", default='data/orders.db')
PROXY_URL = config("PROXY_URL", default=None)

UVICORN_IP = config('UVICORN_IP', default='127.0.0.1') #данные для webhook
UVICORN_PORT = config('UVICORN_PORT', cast=int, default=8000)

REFERRAL_REWARD_RATIO = 0.1 #процент награды, начисляющийся реферерру
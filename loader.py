from config import ACCOUNT_ID, SECRET_KEY, MARZBAN_URL, MARZBAN_USERNAME, MARZBAN_PASSWORD
from services.yookassa_payment import YooKassaClient
from services.marzban import MarzbanAPI
from aiogram import Bot
from config import BOT_TOKEN, PROXY_URL
from aiogram.client.session.aiohttp import AiohttpSession

yookassa_api = YooKassaClient(ACCOUNT_ID, SECRET_KEY)
marzban_api = MarzbanAPI(MARZBAN_URL, MARZBAN_USERNAME, MARZBAN_PASSWORD)

session = AiohttpSession(proxy=PROXY_URL) if PROXY_URL else None
bot = Bot(BOT_TOKEN, session=session)

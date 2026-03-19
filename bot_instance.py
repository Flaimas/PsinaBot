from aiogram import Bot
from config import BOT_TOKEN, PROXY_URL
from aiogram.client.session.aiohttp import AiohttpSession

session = AiohttpSession(proxy=PROXY_URL) if PROXY_URL else None
bot = Bot(BOT_TOKEN, session=session)

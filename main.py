from aiogram import Bot, Dispatcher
from handlers import admin, subscription, start, help
from database import create_db
from config import BOT_TOKEN
from marzban import marzban_api
import asyncio

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(subscription.router)
dp.include_router(admin.router)
dp.include_router(help.router)

async def main():
    await create_db()
    await dp.start_polling(bot)
    await marzban_api.get_token()

if __name__ == '__main__':
    asyncio.run(main())
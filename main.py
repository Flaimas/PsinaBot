from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scheduler import check_vpn_expire, check_expire_users
from handlers import admin, subscription, start, help, submenu, instructions
from database import create_db
from config import BOT_TOKEN, PROXY_URL
from marzban import marzban_api
import asyncio

from aiogram.client.session.aiohttp import AiohttpSession

session = AiohttpSession(proxy=PROXY_URL) if PROXY_URL else None
bot = Bot(token=BOT_TOKEN, session=session)  # порт твоего VPN
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(subscription.router)
dp.include_router(admin.router)
dp.include_router(help.router)
dp.include_router(submenu.router)
dp.include_router(instructions.router)

async def set_commands(bot_: Bot):
    commands = [
        BotCommand(
            command="start",
            description="Главное меню"
        )
    ]
    await bot_.set_my_commands(commands, scope=BotCommandScopeDefault())

async def main():
    await create_db()
    await marzban_api.get_token()
    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)

    schedule = AsyncIOScheduler()
    schedule.add_job(check_vpn_expire, 'cron', hour=10, args=[bot]) #основная база
    schedule.add_job(check_expire_users, 'interval', hours=6, args=[bot]) #база баз

    # schedule.add_job(check_vpn_expire, 'interval', seconds=10, args=[bot]) #Для тестов
    # schedule.add_job(check_expire_users, 'interval', seconds=10, args=[bot]) #Для тестов
    schedule.start()

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scheduler import check_vpn_expire, check_expire_users
from handlers import admin, subscription, start, help, submenu, instructions
from database import create_db
from config import UVICORN_IP, UVICORN_PORT
from marzban import marzban_api
from webhooks.webhook_yoomoney import app
from bot_instance import bot
import asyncio
import payment

dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(subscription.router)
dp.include_router(admin.router)
dp.include_router(help.router)
dp.include_router(submenu.router)
dp.include_router(instructions.router)
dp.include_router(payment.router)

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

    config = uvicorn.Config(app, host=UVICORN_IP, port=UVICORN_PORT, loop='asyncio')
    server = uvicorn.Server(config)
    await asyncio.gather(
        server.serve(),
        dp.start_polling(bot)
    )

if __name__ == '__main__':
    asyncio.run(main())
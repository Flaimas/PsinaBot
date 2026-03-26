import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.scheduler import check_vpn_expire, check_expire_users
from handlers import start, help, submenu, instructions, referral, payment, tariff_menu
from database.database import create_db
from config import UVICORN_IP, UVICORN_PORT, SSL_KEY, SSL_CER
from services.marzban import marzban_api
from webhooks.webhook_yoomoney import app
from bot_instance import bot
import asyncio

dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(help.router)
dp.include_router(submenu.router)
dp.include_router(instructions.router)
dp.include_router(referral.router)
dp.include_router(payment.router)
dp.include_router(tariff_menu.router)

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

    config = uvicorn.Config(app,
                            host=UVICORN_IP,
                            port=UVICORN_PORT,
                            loop='asyncio',
                            ssl_certfile=SSL_CER,
                            ssl_keyfile=SSL_KEY)

    server = uvicorn.Server(config)
    await asyncio.gather(
        server.serve(),
        dp.start_polling(bot)
    )

if __name__ == '__main__':
    asyncio.run(main())
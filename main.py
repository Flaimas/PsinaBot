import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.scheduler import check_vpn_expire, check_expire_users
from handlers import start, help, submenu, instructions, referral, payment, tariff_menu, admin
from database.database import create_db
from config import UVICORN_IP, UVICORN_PORT
from loader import bot, marzban_api, yookassa_api
import asyncio

dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(help.router)
dp.include_router(submenu.router)
dp.include_router(instructions.router)
dp.include_router(referral.router)
dp.include_router(payment.router)
dp.include_router(tariff_menu.router)
dp.include_router(admin.router)

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
    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)

    schedule = AsyncIOScheduler()
    schedule.add_job(check_vpn_expire, 'cron', hour=10, args=[bot]) #основная база
    schedule.add_job(check_expire_users, 'interval', hours=6, args=[bot]) #база баз

    # schedule.add_job(check_vpn_expire, 'interval', seconds=10, args=[bot]) #Для тестов
    # schedule.add_job(check_expire_users, 'interval', seconds=10, args=[bot]) #Для тестов
    schedule.start()

    try:
        print("Бот успешно запущен в режиме polling...")
        await dp.start_polling(bot)
    finally:
        print("Остановка бота... Закрываем сессии.")
        await yookassa_api.close_session()
        print("Сессия ЮКассы закрыта.")
        await marzban_api.close()
        print("Сессия Marzban закрыта.")



if __name__ == '__main__':
    asyncio.run(main())
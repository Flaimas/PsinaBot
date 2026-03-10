from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(F.data == "help")
async def help_user(callback: CallbackQuery):
    await callback.message.reply("Тут должна быть помощь, тоже в разработке!")
from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(F.data == "help")
async def help_user(callback: CallbackQuery):
    await callback.answer()
    await callback.message.reply("Тут должна быть помощь, но пока в разработке :( (not swag)\nДа поможет вам бог!")
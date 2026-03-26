from aiogram import Router, F
from aiogram.types import CallbackQuery

from utils.keyboards import get_help_menu_kb
from utils.text import HELP_TEXT

router = Router()

@router.callback_query(F.data == "help")
async def help_user(callback: CallbackQuery):
    await callback.answer()

    id_user = callback.from_user.id

    await callback.message.edit_text(
        text=HELP_TEXT.format(

            id_user=id_user

        ),
        reply_markup=get_help_menu_kb(),
        parse_mode="HTML")
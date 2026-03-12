from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import SUPPORT_URL

router = Router()

@router.callback_query(F.data == "help")
async def help_user(callback: CallbackQuery):
    await callback.answer()
    id_user = callback.from_user.id
    text = f"""
Возникли трудности?\n
👤 Ваш ID: <code>{id_user}</code>\n
Нажмите на ID 👆, чтобы скопировать и передать агенту поддержки.\n
🔎 Инструкции – база знаний с подробными руководствами по настройке VPN на всех платформах.\n
💬 По любым вопросам можете обращаться в техническую поддержку (10:00 - 20:00 МСК), постараемся помочь как можно быстрее!\n
"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Инструкции", callback_data='instruction'))
    builder.row(InlineKeyboardButton(text="Поддержка", url=SUPPORT_URL))
    builder.row(InlineKeyboardButton(text="Главное меню", callback_data='start'))
    await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")
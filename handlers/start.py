from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from marzban import marzban_api

router = Router()

@router.message(Command('start'))
async def start(message: Message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    status_vpn = f'✅ Активна' if await check_sub(user_id) else f'❌ Не активна'

    await message.answer(
        **text_start_menu(user_name, user_id, status_vpn)
    )

@router.callback_query(F.data == "start")
async def cb_start(callback: CallbackQuery):
    await callback.answer()

    user_name = callback.from_user.first_name
    user_id = callback.from_user.id
    status_vpn = f'✅ Активна' if await check_sub(user_id) else f'❌ Не активна'

    await callback.message.edit_text(
        **text_start_menu(user_name, user_id, status_vpn)
    )

async def check_sub(user_id):
    if await marzban_api.check_user(f"tg_{user_id}"):
        return True
    return False

def text_start_menu(user_name, user_id, status_vpn):
    text = (
        f"Привет, {user_name}!\n"
        f"<blockquote>Ваш ID: {user_id}\n"
        f"Статус VPN: {status_vpn}</blockquote>"
    )
    # Возвращаем словарь со всеми аргументами
    return {
        "text": text,
        "reply_markup": get_start_keyboard(),
        "parse_mode": "HTML"
    }

def get_start_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Купить VPN", callback_data=f"vpn_start"))
    builder.row(InlineKeyboardButton(text="Инструкции", callback_data="instruction"))
    builder.row(InlineKeyboardButton(text="Помощь", callback_data="help"))
    return builder.as_markup()
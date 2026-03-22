from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message,CallbackQuery
from database.database import check_or_register_user, check_use_trial, set_trial_used
from services.marzban import marzban_api
from services.utils import SUB_STATUS
from utils.keyboards import get_trial_error_kb, get_trial_success_kb, get_menu_trial_kb, get_start_kb, \
    get_trial_tech_error_kb
from utils.text import TRIAL_ERROR_TEXT, TRIAL_SUCCESS_TEXT, ERROR_TECH_TEXT, MENU_TRIAL_TEXT

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message, command: CommandObject):
    user_name = message.from_user.first_name
    user_id = message.from_user.id

    referrer_id = command.args
    referrer_id = int(referrer_id) if referrer_id and referrer_id.isdigit() else None
    is_new = await check_or_register_user(user_id, user_name, referrer_id)

    status = None
    if not is_new:
        user_data = await marzban_api.get_user_info(f'tg_{user_id}')
        status = user_data.get('status') if user_data else None

    sub_status_icon = SUB_STATUS.get(status)
    await message.answer(
        **text_start_menu(user_name, user_id, sub_status_icon, status)
    )

@router.callback_query(F.data == "start")
async def start_cb_handler(callback: CallbackQuery):
    await callback.answer()

    user_name = callback.from_user.first_name
    user_id = callback.from_user.id
    user_data = await marzban_api.get_user_info(f'tg_{user_id}')
    if user_data:
        status = user_data.get('status')
    else:
        status = None
    sub_status = SUB_STATUS.get(status)

    await callback.message.edit_text(
        **text_start_menu(user_name, user_id, sub_status, status)
    )

def text_start_menu(user_name, user_id, icon_status, sub_status):
    img_url = "https://i.pinimg.com/736x/e0/10/3e/e0103eba76f37d3d765ca10babf9b34a.jpg"
    # Скрытая ссылка через HTML: пустой символ с гиперссылкой
    hidden_link = f'<a href="{img_url}">&#8203;</a>'
    text = (
        f"{hidden_link}"
        f"Привет, {user_name}!\n"
        f"<blockquote>Ваш ID: <code>{user_id}</code>\n"
        f"Статус подписки: {icon_status}</blockquote>"
    )
    # Возвращаем словарь со всеми аргументами
    return {
        "text": text,
        "reply_markup": get_start_kb(sub_status),
        "parse_mode": "HTML"
    }

@router.callback_query(F.data == 'menu_trial')
async def menu_trial(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(text=MENU_TRIAL_TEXT,
                                     reply_markup=get_menu_trial_kb(),
                                     parse_mode="HTML")


@router.callback_query(F.data == 'trial_subscription')
async def trial_subscription(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    if await check_use_trial(user_id):
        return await callback.message.edit_text(
            text=TRIAL_ERROR_TEXT,
            reply_markup=get_trial_error_kb(),
            parse_mode='HTML'
        )

    if await marzban_api.create_user(f'tg_{user_id}', 3, 'TRIAL', 7158278826):
        await set_trial_used(user_id)
        await callback.message.edit_text(
            text=TRIAL_SUCCESS_TEXT,
            reply_markup=get_trial_success_kb(),
            parse_mode='HTML'
        )
    else:
        await callback.message.answer(text=ERROR_TECH_TEXT,
                                      reply_markup=get_trial_tech_error_kb(),
                                      parse_mode='HTML')
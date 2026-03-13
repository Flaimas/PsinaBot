from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.admin import give_subscription
from marzban import marzban_api

router = Router()

@router.message(Command('start'))
async def start(message: Message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    sub_status = await marzban_api.get_user_info(f'tg_{user_id}')
    if sub_status is None:
        icon_status = "Не приобретен"
    else:
        if sub_status['status'] == 'active':
            icon_status = '✅ Активна'
        else:
            icon_status = f'❌ Не активна'

    await message.answer(
        **text_start_menu(user_name, user_id, icon_status, sub_status)
    )

@router.callback_query(F.data == "start")
async def cb_start(callback: CallbackQuery):
    await callback.answer()

    user_name = callback.from_user.first_name
    user_id = callback.from_user.id
    sub_status = await marzban_api.get_user_info(f'tg_{user_id}')
    if sub_status is None:
        icon_status = "Не приобретен"
    else:
        if sub_status['status'] == 'active':
            icon_status = '✅ Активна'
        else:
            icon_status = f'❌ Не активна'

    await callback.message.edit_text(
        **text_start_menu(user_name, user_id, icon_status, sub_status)
    )

def text_start_menu(user_name, user_id, icon_status, sub_status):
    img_url = "https://i.pinimg.com/736x/e0/10/3e/e0103eba76f37d3d765ca10babf9b34a.jpg"
    # Скрытая ссылка через HTML: пустой символ с гиперссылкой
    hidden_link = f'<a href="{img_url}">&#8203;</a>'
    text = (
        f"{hidden_link}"
        f"Привет, {user_name}!\n"
        f"<blockquote>Ваш ID: {user_id}\n"
        f"Статус VPN: {icon_status}</blockquote>"
    )
    # Возвращаем словарь со всеми аргументами
    return {
        "text": text,
        "reply_markup": get_start_keyboard(sub_status),
        "parse_mode": "HTML"
    }

def get_start_keyboard(sub_status):
    builder = InlineKeyboardBuilder()
    if sub_status:
        builder.row(InlineKeyboardButton(text="Управление подпиской", callback_data=f"menu_sub"))
    if not sub_status:
        builder.row(InlineKeyboardButton(text="Пробная подписка на 3 дня", callback_data=f"menu_trial"))
        builder.row(InlineKeyboardButton(text="Купить VPN", callback_data=f"vpn_start"))

    builder.row(InlineKeyboardButton(text="Инструкции", callback_data="instruction"))
    builder.row(InlineKeyboardButton(text="Помощь", callback_data="help"))
    return builder.as_markup()

@router.callback_query(F.data == 'menu_trial')
async def menu_trial(callback: CallbackQuery):
    await callback.answer()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Активировать пробную подписку", callback_data='trial_subscription'))
    builder.row(InlineKeyboardButton(text="Главное меню", callback_data='start'))
    await callback.message.edit_text(text="Вы можете активировать пробную подписку на 3 дня\n"
                                          "что бы опробовать наш сервис, после истечения срока\n"
                                          "просто продлите её в личном кабинете", parse_mode="HTML", reply_markup=builder.as_markup())

@router.callback_query(F.data == 'trial_subscription')
async def trial_subscription(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    user_name = f'tg_{user_id}'
    data = await marzban_api.get_user_info(user_name)
    if not data:
        await marzban_api.create_user(user_name, 3, 'TRIAL', 7158278826)
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Получить ссылку", callback_data='get_link'))
        await callback.message.edit_text(text="Пробная подписка активирована!", parse_mode="HTML",
                                         reply_markup=builder.as_markup())
        return

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Главное меню", callback_data='start'))
    await callback.message.edit_text(text="Вы уже использовали пробный период!", parse_mode="HTML",
                                     reply_markup=builder.as_markup())
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, CallbackQuery, Message, CopyTextButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ADMIN_IDS
from loader import marzban_api
from utils.keyboards import get_admin_panel_kb, get_tg_access_kb

router = Router()

@router.message(Command('admin'), F.from_user.id.in_(ADMIN_IDS))
async def admin(message: Message):
    await message.answer("<b>Админ панель.</b>",
                         reply_markup=get_admin_panel_kb(),
                         parse_mode='HTML')

@router.callback_query(F.data == 'admin', F.from_user.id.in_(ADMIN_IDS))
async def admin_denied(callback: CallbackQuery):
    await callback.message.edit_text("<b>Админ панель.</b>",
                                     reply_markup=get_admin_panel_kb(),
                                     parse_mode='HTML')

@router.callback_query(F.data == 'tg_access')
async def tg_access(callback: CallbackQuery):
    access_data = await marzban_api.get_user_info('ACCESS')
    try:
        if access_data:
            expire = marzban_api.get_expire_timestamp(1)
            await marzban_api.update_user(
                username='ACCESS',
                expire=expire,
                data_limit=1073741824,
                tariff='NONE',
                reset_strategy='day'
            )
            await marzban_api.reset_user_traffic('ACCESS')
        else:
            await marzban_api.create_user(
                username='ACCESS',
                days=1,
                tariff='NONE',
                data_limit=1073741824,
                data_limit_reset_strategy='day'
            )

        access_link = await marzban_api.get_user_info('ACCESS')
        access_link = access_link.get('subscription_url')

        await callback.message.edit_text(text=f'<b>Ссылка на 1 день, для доступа к ТГ и покупки подписки</b>\n\n'
                                         f'<code>{access_link}</code>',
                                         parse_mode='HTML',
                                         reply_markup=get_tg_access_kb(access_link))

    except Exception as e:
        await callback.message.edit_text(f"Ошибка на стороне API! {e}")
        print(f"Ошибка на стороне API: {e}")



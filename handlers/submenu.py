from aiogram import Router, F
from aiogram.types import InlineKeyboardButton, CallbackQuery, CopyTextButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.marzban import marzban_api
from services.utils import days_left, traffic_left, SUB_STATUS
from prices import PRICES
from utils.keyboards import get_sub_menu_kb, get_no_sub_menu_kb, get_link_kb
from utils.text import NO_SUB_TEXT, SUB_MENU_MAIN_TEXT, GET_LINK_TEXT

router = Router()

@router.callback_query(F.data == 'menu_sub')
async def menu_sub(callback: CallbackQuery):
    await callback.answer()
    tg_id = callback.from_user.id
    user_id = f"tg_{tg_id}"
    user_info = await marzban_api.get_user_info(user_id)
    if not user_info:
        await callback.message.edit_text(
            text=NO_SUB_TEXT,
            eply_markup=get_no_sub_menu_kb(),
            parse_mode="HTML"
        )
        return
    tariff = user_info.get('note')
    expire = user_info.get("expire")

    if not expire:  # None или 0
        days = '∞'
    else:
        days = max(0, days_left(expire))

    traffic = traffic_left(user_info["data_limit"], user_info['used_traffic'])
    status = user_info.get('status')
    sub_status = SUB_STATUS.get(status, None)

    await callback.message.edit_text(
        text=SUB_MENU_MAIN_TEXT.format(

            user_info=tariff,
            tg_id=tg_id,
            sub_status=sub_status,
            days=days,
            traffic=traffic
        ),
        reply_markup=get_sub_menu_kb(tariff),
        parse_mode="HTML"
    )

@router.callback_query(F.data == 'get_link')
async def get_link(callback: CallbackQuery):
    await callback.answer()

    user_name = f'tg_{callback.from_user.id}'
    user_data = await marzban_api.get_user_info(user_name)
    sub_link = user_data.get('subscription_url')

    if sub_link:
        await callback.message.edit_text(
            text=GET_LINK_TEXT.format(sub_link=sub_link),
            reply_markup=get_link_kb(sub_link),
            parse_mode = 'HTML'
        )
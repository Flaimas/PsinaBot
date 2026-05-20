from aiogram import F, Router
from aiogram.types import CallbackQuery

from loader import marzban_api
from services.utils import get_media
from utils.keyboards import get_tariff_menu_kb, get_period_menu_kb, get_tariff_menu_existing_kb
from utils.text import SUB_LIST_TEXT, PERIOD_MENU_TEXT, EXISTING_TARIFF_TEXT

router = Router()

@router.callback_query(F.data == 'tariff_menu')
async def tariff_menu(callback: CallbackQuery):
    await callback.answer()
    tg_id = callback.from_user.id
    user_name = f"tg_{tg_id}"
    try:
        user_info = await marzban_api.get_user_info(user_name)
    except Exception as e:
        print(f"Ошибка API! Чертов марзбан лег: {e}")
        return

    await callback.message.edit_media(
        media=get_media('tariff_menu',SUB_LIST_TEXT),
        reply_markup=get_tariff_menu_kb()
    )


@router.callback_query(F.data.startswith("period_"))
async def period_menu(callback: CallbackQuery):
    await callback.answer()
    tariff = callback.data.split('_')[1]
    await callback.message.edit_media(
        media=get_media('tariff_menu', PERIOD_MENU_TEXT),
        reply_markup=get_period_menu_kb(tariff),
    )

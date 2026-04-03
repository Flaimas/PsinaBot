import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery

from prices import PRICES
from services.payment import get_or_create_payment
from services.utils import get_media
from utils.keyboards import get_create_payment_kb, get_create_payment_error_kb
from utils.text import CREATE_PAYMENT_TEXT, CREATE_PAYMENT_ERROR_TEXT

router = Router()

@router.callback_query(F.data.startswith('pay_'))
async def payment(callback: CallbackQuery):
    await callback.answer()

    id_user = callback.from_user.id
    parts = callback.data.split("_")
    tariff, day = parts[1], int(parts[2])

    payment_url, payment_id = await get_or_create_payment(
        tg_id=id_user,
        tariff_name=tariff,
        day=day
    )

    if payment_url:
        caption = CREATE_PAYMENT_TEXT.format(
            tariff=tariff,
            day=day,
            amount=PRICES.get(tariff).get(str(day))
        )
        await callback.message.edit_media(
            media=get_media('pay_menu', caption=caption),
            reply_markup=get_create_payment_kb(payment_url, tariff)
        )
    else:
        await callback.message.edit_media(
            media=get_media('error_pay',caption=CREATE_PAYMENT_ERROR_TEXT),
            reply_markup=get_create_payment_error_kb(),
        )
        logging.error(f'Ошибка! URL для оплаты не был создан!')
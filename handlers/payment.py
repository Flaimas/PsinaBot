import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.database import get_active_transaction, get_order_info
from loader import yookassa_api
from prices import PRICES
from services.payment import get_or_create_payment, successful_payment
from services.utils import get_media
from utils.keyboards import get_create_payment_kb, get_create_payment_error_kb
from utils.text import CREATE_PAYMENT_TEXT, CREATE_PAYMENT_ERROR_TEXT

logger = logging.getLogger(__name__)
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
            amount=PRICES.get(tariff).get(str(day),)
        )
        await callback.message.edit_media(
            media=get_media('pay_menu', caption=caption),
            reply_markup=get_create_payment_kb(payment_url, tariff, payment_id)
        )
    else:
        await callback.message.edit_media(
            media=get_media('error_pay',caption=CREATE_PAYMENT_ERROR_TEXT),
            reply_markup=get_create_payment_error_kb(),
        )
        logger.error(f'Ошибка! URL для оплаты не был создан!')

processing_payments = set()

@router.callback_query(F.data.startswith('check_payment_'))
async def check_payment(callback: CallbackQuery):
    parts = callback.data.split("_")
    payment_id = parts[2]

    if payment_id in processing_payments:
        await callback.answer("⌛ Уже проверяем, подождите...")
        return
    
    processing_payments.add(payment_id)
    try:
        status_payment = await yookassa_api.find_one(payment_id)
        if not status_payment:
            await callback.answer(text="⚠️ Не удалось связаться с платёжным сервисом. Попробуйте позже.")
            return

        order_info = await get_order_info(payment_id)
        if not order_info:
            await callback.answer(text="⚠️ Заказ не найден. Обратитесь в поддержку.")
            return

        tg_id, tariff, day, db_status = order_info

        if status_payment['status'] == 'succeeded' and db_status == 'pending':
            await successful_payment(tg_id, tariff, day, payment_id)
            await callback.message.delete()
        else:
            await callback.answer(text="⌛ Платеж еще не поступил. Попробуйте через минуту!")

    finally:
        processing_payments.discard(payment_id)
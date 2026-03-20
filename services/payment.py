from datetime import datetime, timezone
from aiogram import Router, F, Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import ACCOUNT_ID, SECRET_KEY
from prices import PRICES
from services.marzban import marzban_api

import uuid
from yookassa import Payment, Configuration

Configuration.account_id = ACCOUNT_ID
Configuration.secret_key = SECRET_KEY

router = Router()

def create_payment(user_id: int,
                   tariff: str, day: int):
    idempotence_key = str(uuid.uuid4())
    amount = PRICES.get(tariff).get(str(day))

    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/PSINA_VPNBOT"
        },
        "capture": True,
        "metadata":{
            "user_id": user_id,
            "tariff": tariff,
            "day": day
        },
        "description": "Оплата подписки"
    }, idempotence_key)
    confirmation_url = payment.confirmation.confirmation_url
    return confirmation_url

async def successful_payment(bot: Bot, user_id: int,
                             tariff: str, day: int):
    success = False
    chat_id = user_id
    user_id = f"tg_{user_id}"
    data_limit = PRICES.get(tariff, {}).get("data_limit")
    user_data = await marzban_api.get_user_info(user_id)
    now_ts = int(datetime.now(timezone.utc).timestamp())

    if user_data:
        status = user_data.get('status')
        current_expire = user_data.get('expire') or now_ts
        if status in ('expired', 'active', 'limited'):
            if status == 'expired' or current_expire < now_ts:
                new_expire = now_ts + (day * 24 * 60 * 60)
            else:
                new_expire = current_expire + (day * 24 * 60 * 60)
            success = await marzban_api.update_user(user_id, new_expire, data_limit, tariff)
    else:
        success = await marzban_api.create_user(user_id, day, tariff, data_limit, 'active')

    if success:

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Управление подпиской", callback_data='menu_sub'))
        builder.row(InlineKeyboardButton(text="Главное меню", callback_data='start'))

        await bot.send_message(chat_id=chat_id, text=f"Подписка {tariff} успешно активирована/продлена на {day} дней!", reply_markup=builder.as_markup())
    else:

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Поддержка", callback_data='help'))

        await bot.send_message(chat_id=chat_id, text="Произошла ошибка при связи с сервером VPN. Свяжитесь с поддержкой.", reply_markup=builder.as_markup())
from datetime import datetime, timezone
from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest

from config import ACCOUNT_ID, SECRET_KEY, REFERRAL_REWARD_RATIO
from database.database import get_referrer, add_reward
from prices import PRICES
from services.marzban import marzban_api

import uuid
from yookassa import Payment, Configuration

from utils.keyboards import get_success_payment_kb, get_failed_payment_kb, get_add_reward_kb
from utils.text import PAYMENT_SUCCESS_TEXT, PAYMENT_FAILED_TEXT, ADD_REWARD_TEXT

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
    user_name = f"tg_{user_id}"
    data_limit = PRICES.get(tariff, {}).get("data_limit")
    user_data = await marzban_api.get_user_info(user_name)
    now_ts = int(datetime.now(timezone.utc).timestamp())

    if user_data:
        status = user_data.get('status')
        current_expire = user_data.get('expire') or now_ts
        if status in ('expired', 'active', 'limited'):
            if status == 'expired' or current_expire < now_ts:
                new_expire = now_ts + (day * 24 * 60 * 60)
            else:
                new_expire = current_expire + (day * 24 * 60 * 60)
            success = await marzban_api.update_user(user_name, new_expire, data_limit, tariff)
    else:
        success = await marzban_api.create_user(user_name, day, tariff, data_limit, 'active')

    if success:
        amount = PRICES.get(tariff,{}).get(str(day), 0)
        reward_amount = int(amount * REFERRAL_REWARD_RATIO)
        print(reward_amount)
        referrer_id = await get_referrer(user_id)
        if reward_amount > 0 and referrer_id:
            await add_reward(reward_amount, referrer_id)
            try:
                await bot.send_message(referrer_id,
                                       text=ADD_REWARD_TEXT.format(reward_amount=reward_amount),
                                       reply_markup=get_add_reward_kb()
                                       )
            except Exception:
                pass

        await bot.send_message(chat_id=user_id,
                               text=PAYMENT_SUCCESS_TEXT.format(tariff=tariff, day=day),
                               reply_markup=get_success_payment_kb())
    else:
        await bot.send_message(chat_id=user_id,
                               text=PAYMENT_FAILED_TEXT,
                               reply_markup=get_failed_payment_kb())
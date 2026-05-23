import logging
from datetime import datetime, timezone, timedelta
from aiogram import Bot
from config import REFERRAL_REWARD_RATIO, ADMIN_IDS
from database.database import get_referrer, add_reward, create_transaction, get_active_transaction, issued_subscription
from prices import PRICES
from loader import marzban_api
import uuid
from loader import yookassa_api, bot
from utils.keyboards import get_success_payment_kb, get_failed_payment_kb, get_add_reward_kb, get_notification_kb
from utils.text import PAYMENT_SUCCESS_TEXT, PAYMENT_FAILED_TEXT, ADD_REWARD_TEXT, NOTIFICATION_BUY_SUB_TEXT, PAYMENT_CHANGESUB_TEXT
from subscription_fabric import change_subscription

async def create_payment(user_id: int, tariff: str, day: int):
    try:
        idempotence_key = str(uuid.uuid4())

        tariff_info = PRICES.get(tariff)
        if not tariff_info:
            logging.error(f'Ошибка! Тариф {tariff} не найден в PRICES')
            return None, None

        amount = tariff_info.get(str(day))
        if not amount:
            logging.error(f'Ошибка! Срок {day} дней не найден для тарифа {tariff_info}!')
            return None, None

        payment = await yookassa_api.create({
            "amount": {
                "value": amount,
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/PSINA_VPNBOT"
            },
            "capture": True,
            "metadata": {
                "user_id": user_id,
                "tariff": tariff,
                "day": day
            },
            "description": "Оплата подписки"
        }, idempotence_key)

        confirmation_url = payment['confirmation']['confirmation_url']
        payment_id = payment['id']

        await create_transaction(
            tg_id=user_id,
            amount=float(amount),
            tariff_name=tariff,
            day=day,
            payment_id=payment_id
        )

        return confirmation_url, payment_id

    except Exception as e:
        logging.error(f'Ошибка при создании платежа: {e}')
        return None, None

async def get_or_create_payment(tg_id: int, tariff_name: str, day: int):
    active_transaction = await get_active_transaction(tg_id, tariff_name, day)

    if active_transaction:
        payment_id, created_at_str = active_transaction
        created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) - created_at < timedelta(minutes=8):
            try:
                existing_payment = await yookassa_api.find_one(payment_id)
                if existing_payment['status'] == 'pending':
                    return existing_payment['confirmation']['confirmation_url'], payment_id
            except Exception as e:
                logging.error(f'Платеж {payment_id} не актуален в ЮKassa: {e}')

    return await create_payment(tg_id, tariff_name, day)

async def successful_payment(user_id: int, tariff: str, day: int, payment_id: str):
    user_name = f"tg_{user_id}"
    tariff_data = PRICES.get(tariff, {})
    data_limit = tariff_data.get("data_limit")

    user_data = await marzban_api.get_user_info(user_name)
    old_tariff = user_data['note'] if user_data else None

    if user_data:
        # new_expire = calculate_new_expire(user_data.get('expire'), day)
        # success = await marzban_api.update_user(user_name, new_expire, data_limit, tariff)
        success = await change_subscription(username=user_name, new_tariff=tariff, day=day)
    else:
        success = await marzban_api.create_user(user_name, day, tariff, data_limit, 'active')

    if success:
        await issued_subscription(payment_id)

        if old_tariff == tariff:
            await bot.send_message(
            chat_id=user_id,
            text=PAYMENT_SUCCESS_TEXT.format(tariff=tariff, day=day),
            reply_markup=get_success_payment_kb()
        )
        else:
            await bot.send_message(
            chat_id=user_id,
            text=PAYMENT_CHANGESUB_TEXT.format(old_tariff=old_tariff, tariff=tariff),
            reply_markup=get_success_payment_kb()
        )

        amount = PRICES.get(tariff,{}).get(str(day), 0)
        reward_amount = int(amount * REFERRAL_REWARD_RATIO)
        referrer_id = await get_referrer(user_id)
        if reward_amount > 0 and referrer_id:
            await add_reward(reward_amount, referrer_id)
            try:
                await bot.send_message(
                    referrer_id,
                    text=ADD_REWARD_TEXT.format(reward_amount=reward_amount),
                    reply_markup=get_add_reward_kb()
                )
            except Exception:
                pass

        if ADMIN_IDS:
            try:
                sub_status = 'продлил' if user_data else 'приобрел'
                await bot.send_message(
                    chat_id=ADMIN_IDS[0],
                    text=NOTIFICATION_BUY_SUB_TEXT.format(user=user_id, sub_status=sub_status),
                    reply_markup=get_notification_kb()
                )
            except Exception as e:
                logging.error(f'Ошибка при уведомлении админа для юзера {user_id}: {e}', exc_info=True)
        else:
            logging.warning("Список ADMIN_IDS пуст, уведомление не отправлено.")

    else:
        await bot.send_message(
            chat_id=user_id,
            text=PAYMENT_FAILED_TEXT,
            reply_markup=get_failed_payment_kb()
        )

def calculate_new_expire(expire: int, day: int):
    now_expire = int(datetime.now(timezone.utc).timestamp())
    if not expire or expire < now_expire:
        return now_expire + (day * 24 * 60 * 60)
    return expire + (day * 24 * 60 * 60)
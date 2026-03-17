from datetime import datetime, timedelta, timezone
from aiogram import Router, F
from aiogram.types import PreCheckoutQuery, Message
from aiogram.types import LabeledPrice
from config import PAYMENT_TOKEN
from prices import PRICES
from marzban import marzban_api

router = Router()

async def create_payment(bot, user_id: int, tariff: str, day: int):
    try:
        print(f"Создаю платёж: {tariff} {day} для {user_id}")
        price = PRICES.get(tariff, {}).get(str(day))
        if not price:
            raise KeyError(f"Price for {tariff}/{day} not found")
        price_in_copeck = price * 100

        label = f"Тариф {tariff.upper()} - {day} дней"
        description = f"Доступ на {day} дней"
        payload = f"payment_{tariff.upper()}_{day}"

        await bot.send_invoice(
            chat_id=user_id,
            title=f"Оплата: {tariff.upper()}",
            description=description,
            payload=payload,
            provider_token=PAYMENT_TOKEN,
            currency="RUB",
            prices=[LabeledPrice(label=label, amount=price_in_copeck)],
            start_parameter="psina-vpn-payment"  # Позволяет перезапустить оплату через deep link
        )
    except Exception as e:
        print(f"Ошибка при создании счета {e}")

@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment(message: Message):
    success = False
    payload = message.successful_payment.invoice_payload
    user_id = f"tg_{message.from_user.id}"

    parts = payload.split("_")
    tariff, day = parts[1], int(parts[2])
    data_limit = PRICES.get(tariff, {}).get("data_limit")
    user_data = await marzban_api.get_user_info(user_id)
    now_ts = int(datetime.now(timezone.utc).timestamp())

    if user_data:
        status = user_data.get('status')
        current_expire = user_data.get('expire') or now_ts
        if status in ('expired', 'active'):
            if status == 'expired' or current_expire < now_ts:
                new_expire = now_ts + (day * 24 * 60 * 60)
            else:
                new_expire = current_expire + (day * 24 * 60 * 60)
            success = await marzban_api.update_user(user_id, new_expire, data_limit, tariff)
    else:
        success = await marzban_api.create_user(user_id, day, tariff, data_limit, 'active')

    if success:
        await message.answer(f"Подписка {tariff} успешно активирована/продлена на {day} дней!")
    else:
        await message.answer("Произошла ошибка при связи с сервером VPN. Свяжитесь с поддержкой.")
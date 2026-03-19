from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from marzban import marzban_api
from datetime import datetime, timezone, timedelta
from database import check_notification, set_notified

async def check_vpn_expire(bot):
    data = await marzban_api.get_all_user()
    if not data:
        return
    users = data['users']
    now = datetime.now(timezone.utc).timestamp()
    three_day = 3 * 24 * 60 * 60

    for user in users:
        expire = user.get('expire')
        username = user.get('username')
        status = user.get('status')
        if not expire or not username.startswith('tg_') or status == 'expired':
            continue
        time_left = expire - now
        if 0 < time_left <= three_day:
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text="Продлить подписку", callback_data="menu_sub"))

            user_id = int(username.replace('tg_',''))
            delta = timedelta(seconds=time_left)
            days = delta.days
            hours = delta.seconds // 3600

            if days > 0:
                word = "день" if days == 1 else "дня" if 2 <= days <= 4 else "дней"
                text = f"⚠️ Ваша подписка истекает через {days} {word}! ⚠️"
            elif hours > 0:
                word = "час" if hours == 1 else "часа" if 2 <= hours <= 4 else "часов"
                text = f"⚠️ Ваша подписка истекает через {hours} {word}! ⚠️"
            else:
                continue

            await bot.send_message(
                chat_id=user_id,
                text=f"{text}\n"
                     f"\n"
                     f"Не хотите потерять доступ к сервису?\n"
                     f"Продлите её прямо сейчас.👇",
                reply_markup=builder.as_markup()
            )

async def check_expire_users(bot):
    data = await marzban_api.get_all_user()
    if not data:
        return
    users = data['users']
    for user in users:
        status = user.get('status')
        username = user.get('username')
        if not status or not username.startswith('tg_'):
            continue
        user_id = int(username.replace('tg_',''))
        notification = await check_notification(user_id)
        if status == 'expired' and notification:
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text="Продлить подписку", callback_data="menu_sub"))
            await bot.send_message(
                chat_id=user_id,
                text=f"Ваша подписка закончилась, доступ отключен.",
                reply_markup=builder.as_markup()
            )
            await set_notified(user_id, 1)
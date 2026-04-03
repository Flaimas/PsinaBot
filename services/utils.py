from datetime import datetime, timezone, timedelta

from aiogram.types import FSInputFile, InputMediaPhoto

from utils.text import MENU_IMAGES


def days_left(expire_timestamp):
    # Переводим timestamp в дату
    expire_date = datetime.fromtimestamp(expire_timestamp, tz=timezone.utc)
    # Берём сегодняшнюю дату
    now = datetime.now(timezone.utc)
    # Вычитаем и берём только дни
    delta = expire_date - now
    return delta.days

def traffic_left(limit_traffic, used_traffic):
    if limit_traffic is None or used_traffic is None:
        return '∞'
    limit_gb = round(limit_traffic / 1024 / 1024 / 1024, 1)
    used_gb = round((used_traffic or 0) / 1024 / 1024 / 1024, 1)
    return f'{used_gb} / {limit_gb} ГБ'

def get_media(photo_name: str, caption: str):
    photo = MENU_IMAGES.get(photo_name)
    return InputMediaPhoto(
        media=photo,
        caption=caption,
        parse_mode='HTML'
    )

SUB_STATUS = {
     'active': '🔥 Активна',
    'expired': '❌ Не активна',
    'limited': '😭 Трафик закончился',
         None: '💀 Не приобретена'
}
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.callback_query(F.data == "instruction")
async def instruction(callback: CallbackQuery):
    await callback.answer()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="iOS", callback_data='ios'), InlineKeyboardButton(text="Android", callback_data='android'))
    builder.row(InlineKeyboardButton(text="Windows", callback_data='windows'), InlineKeyboardButton(text="MacOS", callback_data='mac_os'))
    builder.row(InlineKeyboardButton(text="AndroidTV", callback_data='android_tv'))
    builder.row(InlineKeyboardButton(text="Вернуться в меню", callback_data='start'))

    await callback.message.edit_text("Инструкция по настройке\n"
                                     "\n"
                                     "Выберите Вашу операционную систему:",
                                     reply_markup=builder.as_markup())

INSTRUCTIONS = {
    "ios":"""
<b>Настройка на iOS</b>\n
1. Скачай приложение <a href="https://apps.apple.com/ru/app/v2raytun/id6476628951">v2RayTun</a> из App Store\n
2. Нажми <b>"+"</b> в правом верхнем углу\n
3. Выбери <b>"Импорт из буфера обмена"</b>\n
4. Вставь свою ссылку\n
5. Нажми на профиль → <b>"Подключить"</b>\n
    """,

    "android": """
<b>Настройка VPN на Android</b>\n
1. Скачай приложение <a href="https://play.google.com/store/apps/details?id=com.v2raytun.android">v2RayTun</a> из GooglePlay\n
    1.1 Если GooglePlay не доступен <a href="https://github.com/DigneZzZ/v2raytun/releases/download/5.19.64/v2RayTun_universal.apk">v2RayTun</a> с GitHub.com\n
2. Нажми <b>"+"</b> в правом верхнем углу\n
3. Выбери <b>"Импорт из буфера обмена"</b>\n
4. Вставь свою ссылку\n
5. Нажми на профиль → <b>"Подключить"</b>\n
    """,

    "windows": """
<b>Настройка VPN на Windows</b>\n
1. Скачай <a href="https://github.com/hiddify/hiddify-app/releases/download/v4.1.1/Hiddify-Windows-Portable-x64.zip">Hiddify</a> с GitHub.com\n
2. Нажми <b>"+" → "Буфер обмена"</b>\n
3. Вставь свою ссылку\n
4. Нажми <b>"Подключить"</b>\n
    """,

    "mac_os": """
<b>Настройка VPN на MacOS</b>\n
1. Скачай приложение <a href="https://apps.apple.com/ru/app/v2raytun/id6476628951">v2RayTun</a> из App Store\n
2. Нажми <b>"+"</b> в правом верхнем углу\n
3. Выбери <b>"Импорт из буфера обмена"</b>\n
4. Вставь свою ссылку\n
5. Нажми на профиль → <b>"Подключить"</b>\n
    """,

    "android_tv":"""
<b>Настройка VPN на AndroidTV</b>\n
1. Скачай приложение <a href="https://play.google.com/store/apps/details?id=com.v2raytun.android">v2RayTun</a> из GooglePlay\n
    1.1 Если GooglePlay не доступен <a href="https://github.com/DigneZzZ/v2raytun/releases/download/5.19.64/v2RayTun_universal.apk">v2RayTun</a> с GitHub.com\n
2. Нажми <b>"+"</b> в правом верхнем углу\n
3. Выбери <b>"Импорт из буфера обмена"</b>\n
4. Вставь свою ссылку\n
5. Нажми на профиль → <b>"Подключить"</b>\n
    """
}

@router.callback_query(F.data.in_({"ios", "android", "windows", "mac_os", "android_tv"}))
async def app_install(callback: CallbackQuery):
    await callback.answer()
    text = INSTRUCTIONS[callback.data]
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Назад", callback_data="instruction"))
    builder.row(InlineKeyboardButton(text="Главное меню", callback_data="start"))
    await callback.message.edit_text(text=text, parse_mode="HTML", reply_markup=builder.as_markup())

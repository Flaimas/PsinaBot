from aiogram import Router, F
from aiogram.types import CallbackQuery

from utils.keyboards import get_instructions_kb, get_app_install_kb
from utils.text import INSTRUCTION_HANDLER_TEXT

router = Router()

@router.callback_query(F.data == "instruction")
async def instruction(callback: CallbackQuery):
    await callback.answer()

    await callback.message.edit_text(
        INSTRUCTION_HANDLER_TEXT,
        reply_markup=get_instructions_kb(),
        parse_mode="HTML"
    )

# INSTRUCTIONS = {
#     "ios":"""
# <b>Настройка на iOS</b>\n
# 1. Скачай приложение <a href="https://apps.apple.com/ru/app/v2raytun/id6476628951">v2RayTun</a> из App Store\n
# 2. Нажми <b>"+"</b> в правом верхнем углу\n
# 3. Выбери <b>"Импорт из буфера обмена"</b>\n
# 4. Вставь свою ссылку из бота (ссылку можно получить по кнопке внизу)\n
# 5. Нажми на профиль → <b>"Подключить"</b>\n
#     """,
#
#     "android": """
# <b>Настройка VPN на Android</b>\n
# 1. Скачай приложение <a href="https://play.google.com/store/apps/details?id=com.v2raytun.android">v2RayTun</a> из GooglePlay\n
#     1.1 Если GooglePlay не доступен <a href="https://github.com/DigneZzZ/v2raytun/releases/download/5.19.64/v2RayTun_universal.apk">v2RayTun</a> с GitHub\n
# 2. Нажми <b>"+"</b> в правом верхнем углу\n
# 3. Выбери <b>"Импорт из буфера обмена"</b>\n
# 4. Вставь свою ссылку из бота (ссылку можно получить по кнопке внизу)\n
# 5. Нажми на профиль → <b>"Подключить"</b>\n
#     """,
#
#     "windows": """
# <b>Настройка VPN на Windows</b>\n
# 1. Скачай <a href="https://github.com/Happ-proxy/happ-desktop/releases/latest/download/setup-Happ.x64.exe">Happ</a> с GitHub\n
# 2. Нажми <b>"+" → "Буфер обмена"</b>\n
# 3. Вставь свою ссылку из бота (ссылку можно получить по кнопке внизу)\n
# 4. Нажми <b>"Подключить"</b>\n
#     """,
#
#     "mac_os": """
# <b>Настройка VPN на MacOS</b>\n
# 1. Скачай приложение <a href="https://apps.apple.com/ru/app/v2raytun/id6476628951">v2RayTun</a> из App Store\n
# 2. Нажми <b>"+"</b> в правом верхнем углу\n
# 3. Выбери <b>"Импорт из буфера обмена"</b>\n
# 4. Вставь свою ссылку из бота (ссылку можно получить по кнопке внизу)\n
# 5. Нажми на профиль → <b>"Подключить"</b>\n
#     """,
#
#     "android_tv":"""
# <b>Настройка VPN на AndroidTV</b>\n
# 1. Скачай приложение <a href="https://play.google.com/store/apps/details?id=com.v2raytun.android">v2RayTun</a> из GooglePlay\n
#     1.1 Если GooglePlay не доступен <a href="https://github.com/DigneZzZ/v2raytun/releases/download/5.19.64/v2RayTun_universal.apk">v2RayTun</a> с GitHub.com\n
# 2. Нажми <b>"+"</b> в правом верхнем углу\n
# 3. Выбери <b>"Импорт из буфера обмена"</b>\n
# 4. Вставь свою ссылку из бота (ссылку можно получить по кнопке внизу)\n
# 5. Нажми на профиль → <b>"Подключить"</b>\n
#     """
# }
INSTRUCTIONS = {
    "ios": (
        "<b>Настройка на iOS</b>\n\n"
        "1. Установите приложение <a href='https://apps.apple.com/ru/app/happ-proxy-utility-plus/id6746188973'>Happ Plus</a> из App Store.\n"
        "2. Скопируйте вашу ссылку доступа в боте.\n"
        "3. В приложении нажмите <b>«+»</b> в правом верхнем углу.\n"
        "4. Выберите пункт <b>«Импорт из буфера обмена»</b>.\n"
        "5. Выберите добавленный профиль и нажмите <b>«Подключить»</b>."
    ),

    "android": (
        "<b>Настройка на Android</b>\n\n"
        "1. Установите <a href='https://play.google.com/store/apps/details?id=com.v2raytun.android'>v2RayTun</a> из Google Play.\n"
        "   <i>Если магазин недоступен, скачайте <a href='https://github.com/DigneZzZ/v2raytun/releases/latest'>APK-файл</a> с GitHub.</i>\n"
        "2. Скопируйте вашу ссылку доступа в боте.\n"
        "3. В приложении нажмите <b>«+»</b> в правом верхнем углу.\n"
        "4. Выберите <b>«Импорт из буфера обмена»</b>.\n"
        "5. Нажмите на появившийся профиль для подключения."
    ),

    "windows": (
        "<b>Настройка на Windows</b>\n\n"
        "1. Скачайте программу <a href='https://github.com/Happ-proxy/happ-desktop/releases/latest/download/setup-Happ.x64.exe'>Happ</a> с GitHub.\n"
        "2. Скопируйте вашу ссылку доступа в боте.\n"
        "3. В приложении нажмите <b>«+»</b> → <b>«Буфер обмена»</b>.\n"
        "4. Нажмите кнопку <b>«Подключить»</b> в центре экрана."
    ),

    "mac_os": (
        "<b>Настройка на macOS</b>\n\n"
        "1. Установите <a href='https://apps.apple.com/ru/app/happ-proxy-utility-plus/id6746188973'>Happ Plus</a> из App Store.\n"
        "2. Скопируйте вашу ссылку доступа в боте.\n"
        "3. В приложении нажмите <b>«+»</b> в верхнем углу.\n"
        "4. Выберите <b>«Импорт из буфера обмена»</b>.\n"
        "5. Выберите профиль и активируйте соединение."
    ),

    "android_tv": (
        "<b>Настройка на Android TV</b>\n\n"
        "1. Установите <a href='https://play.google.com/store/apps/details?id=com.v2raytun.android'>v2RayTun</a> через Google Play на ТВ.\n"
        "   <i>Или установите <a href='https://github.com/DigneZzZ/v2raytun/releases/latest'>APK-файл</a> через флешку.</i>\n"
        "2. Скопируйте ссылку доступа в боте и передайте её на ТВ (через QR или спец. приложения).\n"
        "3. В приложении выберите <b>«+»</b> → <b>«Импорт из буфера»</b>.\n"
        "4. Нажмите <b>«Подключить»</b>."
    )
}

@router.callback_query(F.data.in_({"ios", "android", "windows", "mac_os", "android_tv"}))
async def app_install(callback: CallbackQuery):
    await callback.answer()
    text = INSTRUCTIONS[callback.data]
    await callback.message.edit_text(text=text, parse_mode="HTML", reply_markup=get_app_install_kb())

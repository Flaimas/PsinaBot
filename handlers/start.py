from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, FSInputFile
from database.database import check_or_register_user, check_use_trial, set_trial_used, get_referrer
from loader import marzban_api
from services.utils import SUB_STATUS, get_media
from utils.keyboards import get_trial_error_kb, get_trial_success_kb, get_menu_trial_kb, get_start_kb, \
    get_trial_tech_error_kb, get_new_user_kb
from utils.text import TRIAL_ERROR_TEXT, TRIAL_SUCCESS_TEXT, ERROR_TECH_TEXT, MENU_TRIAL_TEXT, NEW_USER_TEXT, \
    MENU_IMAGES, TEXT_START_MENU

router = Router()

@router.message(F.photo)
async def get_photo_id(message: Message):
    photo_id = message.photo[-1].file_id
    await message.answer(text=f'{photo_id}')

@router.message(CommandStart())
async def start_handler(message: Message, command: CommandObject):
    user_name = message.from_user.first_name
    user_id = message.from_user.id

    referrer_id = command.args
    referrer_id = int(referrer_id) if referrer_id and referrer_id.isdigit() else None
    is_new = await check_or_register_user(user_id, user_name, referrer_id)

    if is_new and referrer_id:
        return await message.answer_photo(
            photo=MENU_IMAGES.get('start'),
            caption=NEW_USER_TEXT.format(referrer_id=referrer_id),
            reply_markup=get_new_user_kb(),
            parse_mode = "HTML"
        )

    user_data = await marzban_api.get_user_info(f'tg_{user_id}')
    status = user_data.get('status') if user_data else None

    sub_status_icon = SUB_STATUS.get(status)
    await message.answer_photo(
        photo=MENU_IMAGES.get('start'),
        caption=TEXT_START_MENU.format(user_name=user_name, user_id=user_id, icon_status=sub_status_icon),
        parse_mode='HTML',
        reply_markup=get_start_kb(status)
    )

@router.callback_query(F.data == "start")
async def start_cb_handler(callback: CallbackQuery):
    await callback.answer()

    user_name = callback.from_user.first_name
    user_id = callback.from_user.id
    user_data = await marzban_api.get_user_info(f'tg_{user_id}')
    if user_data:
        status = user_data.get('status')
    else:
        status = None
    sub_status_icon = SUB_STATUS.get(status)

    media = get_media('start', caption=TEXT_START_MENU.format(
        user_name=user_name,
        user_id=user_id,
        icon_status=sub_status_icon)
        )

    await callback.message.edit_media(
        media=media,
        reply_markup=get_start_kb(status)
    )

@router.callback_query(F.data == 'menu_trial')
async def menu_trial(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_media(
        media=get_media('menu_trial', caption=MENU_TRIAL_TEXT),
        reply_markup=get_menu_trial_kb(),
        )

@router.callback_query(F.data == 'trial_subscription')
async def trial_subscription(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    if await check_use_trial(user_id):
        return await callback.message.edit_media(
            media=get_media('error', caption=TRIAL_ERROR_TEXT),
            reply_markup=get_trial_error_kb(),
        )

    if await get_referrer(user_id):
        success = await marzban_api.create_user(f'tg_{user_id}', 10, 'TRIAL', 17179869184)
        if success:
            await set_trial_used(user_id)
            referrer_id = await get_referrer(user_id)
            await marzban_api.update_referrer_sub(referrer_id)

            await callback.bot.send_message(referrer_id, 'Реферал активировал пробную подписку, вы получили дополнительные 7 дней к своей подписке')

            return await callback.message.edit_media(
                media=get_media('trial_sub', caption=TRIAL_SUCCESS_TEXT),
                reply_markup=get_trial_success_kb(),
            )
        return await callback.message.edit_media(
            media=get_media('error',caption=ERROR_TECH_TEXT),
            reply_markup=get_trial_tech_error_kb(),
        )

    if await marzban_api.create_user(f'tg_{user_id}', 3, 'TRIAL', 6442450944):
        await set_trial_used(user_id)
        await callback.message.edit_media(
            media=get_media('trial_sub', caption=TRIAL_SUCCESS_TEXT),
            reply_markup=get_trial_success_kb(),
        )
    else:
        photo = MENU_IMAGES.get('error')
        await callback.message.answer_photo(
            photo=photo,
            caption=ERROR_TECH_TEXT,
            reply_markup=get_trial_tech_error_kb(),
            parse_mode='HTML')


@router.message(F.photo)
async def get_photo_id(message: Message):
    # message.photo — это список разных размеров одного фото.
    # Последний элемент [-1] — самый качественный.
    photo_id = message.photo[-1].file_id
    await message.answer(f"<code>{photo_id}</code>", parse_mode="HTML")
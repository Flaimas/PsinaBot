from aiogram.utils.deep_linking import create_start_link
from aiogram.types import CallbackQuery
from aiogram import Router, F
from bot_instance import bot
from utils.keyboards import get_referral_kb
from utils.text import REFERRAL_HANDLER_TEXT

router = Router()

@router.callback_query(F.data == 'referral')
async def referral_handler(callback: CallbackQuery):
    link = await create_start_link(bot, str(callback.from_user.id), encode=False)

    await callback.message.edit_text(text=REFERRAL_HANDLER_TEXT.format(link=link),
                                     reply_markup=get_referral_kb(link),
                                     parse_mode="HTML")
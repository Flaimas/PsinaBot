from aiogram.utils.deep_linking import create_start_link
from aiogram.types import CallbackQuery
from aiogram import Router, F
from bot_instance import bot
from database.database import get_count_referrals, get_reward_balance
from utils.keyboards import get_referral_kb
from utils.text import REFERRAL_HANDLER_TEXT

router = Router()

@router.callback_query(F.data == 'referral')
async def referral_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    link = await create_start_link(bot, str(user_id), encode=False)
    count_ref = await get_count_referrals(user_id)
    reward_balance = await get_reward_balance(user_id)

    await callback.message.edit_text(
        text=REFERRAL_HANDLER_TEXT.format(

            link=link,
            count_ref=count_ref,
            reward_balance=reward_balance
        ),

        reply_markup=get_referral_kb(link),
        parse_mode="HTML")
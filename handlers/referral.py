from aiogram.utils.deep_linking import decode_payload, create_start_link
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from bot_instance import bot

router = Router()

@router.callback_query(F.data == 'referral')
async def referral_handler(callback: CallbackQuery):
    link = await create_start_link(bot, str(callback.from_user.id), encode=False)
    await callback.message.edit_text(text=f'Реферальная система бла бла бла:\n'
                                          f'Ваша реферальная ссылка:\n'
                                          f'{link}')
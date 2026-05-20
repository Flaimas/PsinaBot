from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(F.data.startswith("buy_data_"))
async def buy_data(callback: CallbackQuery):
    await callback.answer()
    parts = callback.data.split('_')
    data_amount = parts[2]
     

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
from config import BOT_TOKEN
from marzban import create_user, delete_user, get_user_link, check_user

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def start(message: Message):
    kb = [
        [KeyboardButton(text='Подписка'), KeyboardButton(text='Помощь')],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder='Хз зачем, но я так могу')

    await message.answer('ЗДАРОВА, ДРУК, Я ХОЧУ ТВОИХ ДЕНЕГ!', reply_markup=keyboard)

@dp.message(F.text.lower() == 'подписка')
async def subscription_user(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Подписка 1 месяц - 150р",
        callback_data="subscription_30")
    )
    builder.add(InlineKeyboardButton(
        text='Подписка 3 месяца - 400р',
        callback_data="subscription_90"
    ))
    await message.answer(
        "Подписка",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data.in_({"subscription_30", "subscription_90"}))
async def subscription(callback: CallbackQuery):
    days = int(callback.data.split('_')[-1])
    username = f'tg_{callback.from_user.id}'
    if not check_user(username):
        create_user(username, days)
        user_url = str(get_user_link(f'tg_{callback.from_user.id}'))
        await callback.message.answer(user_url)
    else:
        await callback.message.answer('Подписка уже получена!')

@dp.message(F.text.lower() == 'помощь')
async def help_user(message: Message):
    await message.reply("Тут должна быть помощь, тоже в разработке!")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
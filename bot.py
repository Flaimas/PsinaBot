from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
from config import BOT_TOKEN
from marzban import create_user, delete_user, get_user_link, check_user
from database import add_order, create_db

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def start(message: Message):
    kb = [
        [KeyboardButton(text='Подписка'), KeyboardButton(text='Помощь')],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder='Хз зачем, но я так могу')

    await message.answer('ЗДАРОВА, ДРУК, Я ХОЧУ ТВОИХ ДЕНЕГ!', reply_markup=keyboard)

def get_main_subscription_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="STANDART (3 устр.)", callback_data="sub_STANDART"))
    builder.row(InlineKeyboardButton(text='GO (5 устр.)', callback_data="sub_GO"))
    builder.row(InlineKeyboardButton(text='PRO (9 устр.)', callback_data="sub_PRO"))
    return builder.as_markup()

@dp.message(F.text.lower() == 'подписка')
async def cmd_subscription(message: Message):
    await message.answer(
        "Выберите тарифный план:",
        reply_markup=get_main_subscription_keyboard()
    )

@dp.callback_query(F.data == 'подписка')
async def back_to_subscription(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Выберит тарифный план:",
        reply_markup=get_main_subscription_keyboard()
    )

@dp.callback_query(F.data.startswith("sub_"))
async def cb_subscription_details(callback: CallbackQuery):
    # Убираем "часики" на кнопке
    await callback.answer()

    # Получаем тариф из callback_data (например, STANDART)
    tariff = callback.data.split("_")[1]

    # Редактируем старое сообщение вместо отправки нового
    await callback.message.edit_text(
        f"Вы выбрали тариф: {tariff}\nВыберите срок подписки.",
        reply_markup=inline_buy_subscription(tariff)  # Или другая клавиатура для оплаты
    )
@dp.callback_query(F.data.startswith("time_"))
async def time_subscription(callback: CallbackQuery):
    await callback.answer()
    days = callback.data.split('_')[-1]
    tariff = callback.data.split("_")[-2]
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Купить', callback_data=f"pay_{tariff}_{days}"))
    builder.row(InlineKeyboardButton(text='Назад', callback_data=f"sub_{tariff}"))
    await callback.message.edit_text(text=f'Тариф {tariff}\nСроком {days} дней.', reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("pay_"))
async def pay_subscription(callback: CallbackQuery):
    await callback.answer()
    price = {
        "GO": {
            "30": "149",
            "90": "429",
            "180": "799",
            "360": "1499"
        },
        "STANDART": {
            "30": "249",
            "90": "709",
            "180": "1339",
            "360": "2499"
        },
        "PRO":{
            "30": "399",
            "90": "1139",
            "180": "2149",
            "360": "4049"
        }
    }
    days = callback.data.split('_')[-1]
    tariff = callback.data.split("_")[-2]
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Я оплатил", callback_data=f'cp_{callback.from_user.id}_{tariff}_{days}'))
    builder.row(InlineKeyboardButton(text="Назад", callback_data=f"time_{tariff}_{days}"))
    await callback.message.edit_text(
        f"ТУТ ДОЛЖНЫ БЫТЬ РЕКВИЗИТЫ\n"
        f"Подписка {tariff} - {days} дней.\n"
        f"К оплате: {price[tariff][days]} рублей.",
        reply_markup=builder.as_markup()
                                     )
@dp.callback_query(F.data.startswith("cp_"))
async def cp_subscription(callback: CallbackQuery):
    await callback.answer()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Крутяк", callback_data=f"пока нихуя"))

    user_id = int(callback.data.split("_")[-3])
    tariff = callback.data.split("_")[-2]
    days = int(callback.data.split("_")[-1])
    await add_order(user_id, tariff, days)

    await callback.message.edit_text(
        "Платеж принят в обработку, в скором времени ваша подписка станет активной!",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data.startswith("buy_"))
async def give_subscription(callback: CallbackQuery):
    await callback.answer() #убираем часики
    days = int(callback.data.split('_')[-1])
    username = f'tg_{callback.from_user.id}'
    if not check_user(username):
        create_user(username, days)
        user_url = get_user_link(f'tg_{callback.from_user.id}')
        await callback.message.answer(user_url)
    else:
        await callback.message.answer('Подписка уже получена!')

def inline_buy_subscription(tariff):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="1 месяц", callback_data=f"time_{tariff}_30"))
    builder.row(InlineKeyboardButton(text="3 месяца", callback_data=f"time_{tariff}_90"))
    builder.row(InlineKeyboardButton(text="6 месяцев", callback_data=f"time_{tariff}_180"))
    builder.row(InlineKeyboardButton(text="12 месяцев", callback_data=f"time_{tariff}_360"))
    builder.row(InlineKeyboardButton(text="Назад", callback_data=f"подписка"))
    return builder.as_markup()

@dp.message(F.text.lower() == 'помощь')
async def help_user(message: Message):
    await message.reply("Тут должна быть помощь, тоже в разработке!")

async def main():
    await dp.start_polling(bot)
    await create_db()

if __name__ == '__main__':
    asyncio.run(main())
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
from config import BOT_TOKEN, ADMIN_ID
from marzban import create_user, delete_user, get_user_link, check_user
from database import add_order, create_db, get_order, check_pending_order, get_orders_list, db_delete_user, update_order_status

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def start(message: Message):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Купить VPN", callback_data="vpn_start"))
    builder.row(InlineKeyboardButton(text="Инструкции", callback_data="instruction"))
    builder.row(InlineKeyboardButton(text="Помощь", callback_data="help"))

    await message.answer(f"Привет, {message.from_user.first_name}!"
                         f"<blockquote>Ваш ID: {message.from_user.id}\n"
                         f"Статус VPN: [ДОБАВИТЬ ПРОВЕРКУ]</blockquote>",
                         reply_markup=builder.as_markup(),
                         parse_mode="HTML")

@dp.message(Command('admin'), F.from_user.id == int(ADMIN_ID))
async def admin_panel(message: Message):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Список заказов", callback_data="admin_order_list"))
    await message.answer('Добро пожаловать в админку!', reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("buy_"))
async def give_subscription(callback: CallbackQuery):
    await callback.message.delete()
    print("Сюда я вхожу")
    await callback.answer() #убираем часики
    order = await get_order(int(callback.data.split("_")[-1]))
    order_id = order[0]
    user_id = order[1]
    tariff = order[2]
    days = order[3]
    username = f'tg_{user_id}'
    await update_order_status(int(order_id), 'issued')

    if not check_user(username):
        create_user(username, days)
        user_url = get_user_link(username)
        await callback.bot.send_message(
            chat_id=user_id,  # ID того, кому летит ссылка
            text=f"Ваша ссылка готова: {user_url}"
        )
    else:
        await callback.message.answer('Подписка уже получена!')


def get_main_subscription_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="STANDART (3 устр.)", callback_data="sub_STANDART"))
    builder.row(InlineKeyboardButton(text='GO (5 устр.)', callback_data="sub_GO"))
    builder.row(InlineKeyboardButton(text='PRO (9 устр.)', callback_data="sub_PRO"))
    return builder.as_markup()

@dp.callback_query(F.data == 'vpn_start')
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


@dp.callback_query(F.data == 'admin_order_list')
async def admin_order_list(callback: CallbackQuery):
    orders = await get_orders_list()

    if not orders:
        await callback.answer("Список заказов пуст")
        return

    await callback.answer()  # Убираем часики

    for order in orders:
        # Предположим, твоя функция возвращает (id, user_id, tariff, days)
        # ВАЖНО: передавай в кнопку именно ID ЗАКАЗА, а не user_id
        order_db_id, user_id, tariff, days = order[0], order[1], order[2], order[3]

        await callback.message.answer(
            text=f"📦 **Заказ №{order_db_id}**\n"
                 f"👤 Пользователь: `{user_id}`\n"
                 f"💎 Тариф: {tariff} ({days} дн.)",
            reply_markup=accept_menu(order_db_id),  # Передаем только ID заказа
            parse_mode="Markdown"
        )

def accept_menu(db_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Подтвердить", callback_data=f"buy_{db_id}"))
    builder.row(InlineKeyboardButton(text="Отклонить", callback_data=f"order_delete_{db_id}"))
    return builder.as_markup()

@dp.callback_query(F.data.startswith("order_delete_"))
async def order_delete(callback: CallbackQuery):
    await callback.answer()
    order_id = int(callback.data.split("_")[-1])
    await db_delete_user(order_id)
    await callback.message.delete()

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

    user_id = int(callback.data.split("_")[-3])
    tariff = callback.data.split("_")[-2]
    days = int(callback.data.split("_")[-1])
    existing_order = await check_pending_order(user_id)
    if existing_order:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="ОК, БРО БРО БРО, ЖДУ!", callback_data="wait_ok"))
        await callback.message.edit_text("У вас уже есть оплаченный заказ, дождитесь подтверждения!",
                                         reply_markup= builder.as_markup()
                                         )
        return

    await add_order(user_id, tariff, days)#добавление заказа в БД

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Перейти к списку", callback_data=f"admin_order_list"))
    await callback.bot.send_message(chat_id=int(ADMIN_ID),
                                    text=f"Пользователь {user_id} оплатил подписку {tariff} на {days} дней!",
                                    reply_markup=builder.as_markup()
                                    )

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Крутяк", callback_data=f"НИХУЯ_ТУТ_НЕТ"))
    await callback.message.edit_text(
        "Платеж принят в обработку, в скором времени ваша подписка станет активной!",
        reply_markup=builder.as_markup()
    )

def inline_buy_subscription(tariff):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="1 месяц", callback_data=f"time_{tariff}_30"))
    builder.row(InlineKeyboardButton(text="3 месяца", callback_data=f"time_{tariff}_90"))
    builder.row(InlineKeyboardButton(text="6 месяцев", callback_data=f"time_{tariff}_180"))
    builder.row(InlineKeyboardButton(text="12 месяцев", callback_data=f"time_{tariff}_360"))
    builder.row(InlineKeyboardButton(text="Назад", callback_data=f"vpn_start"))
    return builder.as_markup()

@dp.callback_query(F.data == "help")
async def help_user(callback: CallbackQuery):
    await callback.message.reply("Тут должна быть помощь, тоже в разработке!")

async def main():
    await create_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
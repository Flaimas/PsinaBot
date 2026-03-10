from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
from config import BOT_TOKEN, ADMIN_ID
from marzban import marzban_api
from database import add_order, create_db, get_order, check_pending_order, get_orders_list, db_delete_user, update_order_status

router = Router()

@router.message(Command('admin'), F.from_user.id == int(ADMIN_ID))
async def admin_panel(message: Message):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Список заказов", callback_data="admin_order_list"))
    builder.row(InlineKeyboardButton(text="Выход", callback_data="start"))
    await message.answer('Добро пожаловать в админку!', reply_markup=builder.as_markup())

@router.callback_query(F.data == 'admin_order_list')
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

@router.callback_query(F.data.startswith("order_delete_"))
async def order_delete(callback: CallbackQuery):
    await callback.answer()
    order = await get_order(int(callback.data.split("_")[2]))
    order_id = order[0]
    user_id = order[1]

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Главное меню', callback_data=f'start'))
    builder.row(InlineKeyboardButton(text='Поддержка', callback_data='help'))

    await callback.bot.send_message(chat_id=user_id, text='Администратор не подтвердил ваш платеж..', reply_markup=builder.as_markup())
    await db_delete_user(order_id)
    await callback.message.delete()

def accept_menu(db_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Подтвердить", callback_data=f"buy_{db_id}"))
    builder.row(InlineKeyboardButton(text="Отклонить", callback_data=f"order_delete_{db_id}"))
    return builder.as_markup()

@router.callback_query(F.data.startswith("buy_"))
async def give_subscription(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer() #убираем часики
    order = await get_order(int(callback.data.split("_")[1]))
    order_id = order[0]
    user_id = order[1]
    tariff = order[2]
    days = order[3]
    username = f'tg_{user_id}'
    await update_order_status(int(order_id), 'issued')

    if not await marzban_api.check_user(username):
        await marzban_api.create_user(username, days)
        user_url = await marzban_api.get_user_link(username)
        await callback.bot.send_message(
            chat_id=user_id,  # ID того, кому летит ссылка
            text=f"Ваша ссылка готова: {user_url}"
        )
    else:
        await callback.message.answer('Подписка уже получена!')
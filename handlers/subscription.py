from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import ADMIN_ID, MANUAL_PAYMENT
from database import add_order, check_pending_order
from marzban import marzban_api
from prices import PRICES
from payment import create_payment

router = Router()

@router.callback_query(F.data == 'vpn_start')
async def back_to_subscription(callback: CallbackQuery):
    await callback.answer()
    user_id = f'tg_{callback.from_user.id}'
    status_vpn = await marzban_api.check_user(user_id)
    if status_vpn:

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Управление подпиской", callback_data="menu_sub"))
        builder.row(InlineKeyboardButton(text="Назад", callback_data='start'))

        await callback.message.edit_text(
            f"У вас уже подключен тарифный план,\n"
            f"используйте меню управления подпиской!",
            reply_markup=builder.as_markup()
        )
        return

    await callback.message.edit_text(
        "Выберит тарифный план:",
        reply_markup=get_main_subscription_keyboard()
    )

def get_main_subscription_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="STANDART (3 устр.)", callback_data="sub_STANDART"))
    builder.row(InlineKeyboardButton(text='GO (5 устр.)', callback_data="sub_GO"))
    builder.row(InlineKeyboardButton(text='PRO (9 устр.)', callback_data="sub_PRO"))
    builder.row(InlineKeyboardButton(text='Назад', callback_data="start"))
    return builder.as_markup()

@router.callback_query(F.data.startswith("sub_"))
async def cb_subscription_details(callback: CallbackQuery):
    # Убираем "часики" на кнопке
    await callback.answer()

    # Получаем тариф из callback_data (например, STANDART)
    tariff = callback.data.split("_")[1]

    # Редактируем старое сообщение вместо отправки нового
    await callback.message.edit_text(
        f"Вы выбрали тариф: {tariff}\nВыберите срок подписки.",
        reply_markup=inline_subscription_list(tariff)  # Или другая клавиатура для оплаты
    )

def inline_subscription_list(tariff):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=f"1 месяц - {PRICES[tariff]['30']} ₽", callback_data=f"time_{tariff}_30"))
    builder.row(InlineKeyboardButton(text=f"3 месяца - {PRICES[tariff]['90']} ₽", callback_data=f"time_{tariff}_90"))
    builder.row(InlineKeyboardButton(text=f"6 месяцев - {PRICES[tariff]['180']} ₽", callback_data=f"time_{tariff}_180"))
    builder.row(InlineKeyboardButton(text=f"12 месяцев - {PRICES[tariff]['360']} ₽", callback_data=f"time_{tariff}_360"))
    builder.row(InlineKeyboardButton(text="Назад", callback_data=f"vpn_start"))
    return builder.as_markup()

@router.callback_query(F.data.startswith("time_"))
async def time_subscription(callback: CallbackQuery):
    await callback.answer()

    tariff = callback.data.split("_")[1]
    days = callback.data.split('_')[2]

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Купить', callback_data=f"pay_{tariff}_{days}"))
    builder.row(InlineKeyboardButton(text='Назад', callback_data=f"sub_{tariff}"))

    await callback.message.edit_text(text=f'Тариф: {tariff}\n'
                                          f'Срок: {days} дней.\n'
                                          f'Стоимость: {PRICES[tariff][days]} ₽',
                                     reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("pay_"))
async def pay_subscription(callback: CallbackQuery):
    await callback.answer()

    id_user = callback.from_user.id
    parts = callback.data.split("_")
    tariff, day = parts[1], int(parts[2])

    if MANUAL_PAYMENT:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Я оплатил", callback_data=f'cp_{callback.from_user.id}_{tariff}_{day}'))
        builder.row(InlineKeyboardButton(text="Назад", callback_data=f"time_{tariff}_{day}"))
        await callback.message.edit_text(
            f"ТУТ ДОЛЖНЫ БЫТЬ РЕКВИЗИТЫ\n"
            f"\n"
            f"Подписка {tariff} - {day} дней.\n"
            f"К оплате: {PRICES[tariff][day]} ₽",
            reply_markup=builder.as_markup()
        )
    else:
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass
        await create_payment(callback.bot, id_user, tariff, day)  # создание платежа

@router.callback_query(F.data.startswith("cp_"))
async def cp_subscription(callback: CallbackQuery):
    await callback.answer()

    user_id = int(callback.data.split("_")[1])
    tariff = callback.data.split("_")[2]
    days = int(callback.data.split("_")[3])
    existing_order = await check_pending_order(user_id) #проверка - существуют ли необработанные платежи
    # existing_sub = await ()

    if existing_order:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Главное меню", callback_data="start"))
        await callback.message.edit_text("У вас уже есть оплаченный заказ, дождитесь подтверждения!",
                                         reply_markup= builder.as_markup()
                                         )
        return

    await add_order(user_id, tariff, days) #добавление заказа в БД

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Перейти к списку", callback_data=f"admin_order_list"))
    await callback.bot.send_message(chat_id=int(ADMIN_ID),
                                    text=f"Пользователь {user_id} оплатил подписку {tariff} на {days} дней!",
                                    reply_markup=builder.as_markup()
                                    )

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Главное меню", callback_data=f"start"))
    await callback.message.edit_text(
        "Платеж принят в обработку, в скором времени ваша подписка станет активной!",
        reply_markup=builder.as_markup()
    )
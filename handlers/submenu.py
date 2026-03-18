from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton, CallbackQuery, CopyTextButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import ADMIN_ID, MANUAL_PAYMENT
from database import add_expire_order, check_extend_order, check_order
from marzban import marzban_api
from payment import create_payment
from utils import days_left, traffic_left, SUB_STATUS
from prices import PRICES

router = Router()

@router.callback_query(F.data == 'menu_sub')
async def menu_sub(callback: CallbackQuery):
    await callback.answer()
    user_id = f"tg_{callback.from_user.id}"
    user_info = await marzban_api.get_user_info(user_id)
    if not user_info:
        await callback.message.edit_text(
            "У вас нет активной подписки!",
            reply_markup=get_no_sub_menu() # кнопка "Купить"
        )
        return
    tariff = user_info.get('note')
    expire = user_info.get("expire")

    if not expire:  # None или 0
        days = '∞'
    else:
        days = max(0, days_left(expire))

    traffic = traffic_left(user_info["data_limit"], user_info['used_traffic'])
    status = user_info.get('status')  # всего два положения, временный костыль, нужно будет создать функцию
    sub_status = SUB_STATUS.get(status, None)

    text = (
        f"Подписка {user_info['note']}!\n"
        f"<blockquote>Ваш ID: <code>{callback.from_user.id}</code>\n"
        f"Статус подписки: {sub_status}\n"
        f"Дней осталось: {days}\n"
        f"Трафик: {traffic}</blockquote>"
    )
    await callback.message.edit_text(text=text, reply_markup=get_sub_menu(tariff), parse_mode="html")

def get_sub_menu(tariff):
    builder = InlineKeyboardBuilder()
    if tariff == 'TRIAL':
        builder.row(InlineKeyboardButton(text="Изменить тариф", callback_data='new_tariff'))
    else:
        builder.row(InlineKeyboardButton(text="Продлить подписку", callback_data='add_days'),
                    InlineKeyboardButton(text="Изменить тариф", callback_data='new_tariff'))

    builder.row(InlineKeyboardButton(text="Получить ссылку", callback_data='get_link'))
    builder.row(InlineKeyboardButton(text="Главное меню", callback_data='start'))
    return builder.as_markup()

def get_no_sub_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Купить VPN", callback_data='vpn_start'))
    builder.row(InlineKeyboardButton(text="⤿ Назад", callback_data='start'))
    return builder.as_markup()


@router.callback_query(F.data == 'add_days')
async def add_days(callback: CallbackQuery):
    await callback.answer()
    user_id = f"tg_{callback.from_user.id}"
    user_info = await marzban_api.get_user_info(user_id)

    if not user_info:
        await callback.message.edit_text("У вас нет активной подписки!", reply_markup=get_no_sub_menu())
        return

    tariff = user_info['note']
    await callback.message.edit_text(
        text=f'Выберите на сколько требуется продлить подписку {tariff}',
        reply_markup=get_price_subscription(tariff)
    )


def get_price_subscription(tariff):
    tariff = str(tariff)
    # Базовая цена за 30 дней, чтобы от неё считать выгоду
    base_price_30 = PRICES[tariff]['30']

    builder = InlineKeyboardBuilder()

    periods = [
        ("1 месяц", "30", 1),
        ("3 месяца", "90", 3),
        ("6 месяцев", "180", 6),
        ("12 месяцев", "360", 12)
    ]

    for text, days, month_count in periods:
        current_price = PRICES[tariff][days]

        # Считаем выгоду: (1 - (цена_периода / (цена_за_месяц * кол_во_месяцев))) * 100
        # Пример для 3 месяцев: (1 - (429 / (149 * 3))) * 100 = 4%
        discount = int((1 - (current_price / (base_price_30 * month_count))) * 100)

        discount_str = f" (-{discount}%)" if discount > 0 else ""

        builder.row(InlineKeyboardButton(
            text=f"{text} - {current_price} ₽{discount_str}",
            callback_data=f"extend_{tariff}_{days}"
        ))

    builder.row(InlineKeyboardButton(text="⤿ Назад", callback_data="menu_sub"))
    return builder.as_markup()

@router.callback_query(F.data.startswith("extend_"))
async def extend_sub(callback: CallbackQuery):
    await callback.answer()
    tariff = callback.data.split("_")[1]
    days = callback.data.split("_")[2]

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Оплатить", callback_data=f"es_{tariff}_{days}"))
    builder.row(InlineKeyboardButton(text="⤿ Назад", callback_data="add_days"))

    await callback.message.edit_text(
        text=f"Продлить подписку {tariff} на {days} дней?\n"
             f"Цена: {PRICES[tariff][days]} ₽",
        reply_markup=builder.as_markup()

    )

@router.callback_query(F.data.startswith("es_"))
async def change_sub_pay(callback: CallbackQuery):
    await callback.answer()

    id_user = callback.from_user.id
    parts = callback.data.split("_")
    tariff, day = parts[1], int(parts[2])

    if MANUAL_PAYMENT:
        tariff = callback.data.split("_")[1]
        days = callback.data.split('_')[2]

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Я оплатил", callback_data=f'cp_{callback.from_user.id}_{tariff}_{days}'))
        builder.row(InlineKeyboardButton(text="⤿ Назад", callback_data=f"time_{tariff}_{days}"))
        await callback.message.edit_text(
            f"ТУТ ДОЛЖНЫ БЫТЬ РЕКВИЗИТЫ\n"
            f"\n"
            f"Подписка {tariff} - {days} дней.\n"
            f"К оплате: {PRICES[tariff][days]} ₽",
            reply_markup=builder.as_markup()
        )
    else:
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass
        await create_payment(callback.bot, id_user, tariff, day)  # создание платежа

@router.callback_query(F.data.startswith("PAY_EXTEND_"))
async def pay_changed(callback: CallbackQuery):
    await callback.answer()
    tariff = callback.data.split("_")[2]
    days = callback.data.split("_")[3]
    user_id = callback.from_user.id
    user_name = f"tg_{user_id}"
    user_info = await marzban_api.get_user_info(user_name)
    db_check = await check_extend_order(user_id)
    if db_check:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Главное меню", callback_data='start'))
        await callback.message.edit_text("Подождите пока администратор подтвердит оплату!", reply_markup=builder.as_markup())
        return
    if user_info:
        await add_expire_order(user_id, tariff, days, "extend")
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Главное меню", callback_data='start'))
        await callback.message.edit_text("Платеж принят в обработку, в скором времени ваша подписка станет активной!", reply_markup=builder.as_markup())
        await callback.bot.send_message(text=f"Пользователь {user_id} продлил подписку {tariff} на {days} дней.", chat_id=ADMIN_ID)

@router.callback_query(F.data == 'new_tariff')
async def new_tariff(callback: CallbackQuery):
    await callback.answer()
    user_id = f"tg_{callback.from_user.id}"
    user_info = await marzban_api.get_user_info(user_id)

    if user_info.get('status') != 'extend' and user_info.get('note') != 'TRIAL':
        builder = InlineKeyboardBuilder().row(InlineKeyboardButton(text="Помощь", callback_data='help'), InlineKeyboardButton(text="Понятно", callback_data='start'))
        await callback.message.edit_text(text="<blockquote>Внимание‼️\n"
                                              "Изменить тариф можно только после окончания текущего!\n"
                                              "\nЛибо обратитесь за помощью в поддержку.</blockquote>", reply_markup=builder.as_markup(), parse_mode="HTML")
        return

    if user_info:
        tariff = user_info['note'] if user_info is not None else False
        await callback.message.edit_text(text=f'Выберите подписку, ваша текущая {tariff}\n'
                                              f'<blockquote><b>STANDART</b> — базовый тариф для личного использования. До 3 устройств, 200 ГБ трафика в месяц.\n'
                                              f'\n'
                                              f'<b>GO</b> — оптимальный выбор для активных пользователей. До 5 устройств, 400 ГБ трафика в месяц.\n'
                                              f'\n'
                                              f'<b>PRO</b> — максимальный тариф для интенсивного использования. До 9 устройств, 800 ГБ трафика в месяц.</blockquote>',
                                         reply_markup=get_change_subscription(), parse_mode='HTML')
        return
    await callback.message.edit_text(text='Пользователь не найден :(', reply_markup=get_no_sub_menu())

def get_change_subscription():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="STANDART (3 устр.)", callback_data="change_sub_STANDART"))
    builder.row(InlineKeyboardButton(text='GO (5 устр.)', callback_data="change_sub_GO"))
    builder.row(InlineKeyboardButton(text='PRO (9 устр.)', callback_data="change_sub_PRO"))
    builder.row(InlineKeyboardButton(text='⤿ Назад', callback_data="menu_sub"))
    return builder.as_markup()

@router.callback_query(F.data.startswith("change_sub_"))
async def change_sub(callback: CallbackQuery):
    await callback.answer()
    tariff = callback.data.split('_')[2]
    await callback.message.edit_text(text=f"Выберите срок подписки {tariff}", reply_markup=get_ch_tariff(tariff))

def get_ch_tariff(tariff):
    tariff = str(tariff)
    # Базовая цена за 30 дней, чтобы от неё считать выгоду
    base_price_30 = PRICES[tariff]['30']

    builder = InlineKeyboardBuilder()

    periods = [
        ("1 месяц", "30", 1),
        ("3 месяца", "90", 3),
        ("6 месяцев", "180", 6),
        ("12 месяцев", "360", 12)
    ]

    for text, days, month_count in periods:
        current_price = PRICES[tariff][days]

        # Считаем выгоду: (1 - (цена_периода / (цена_за_месяц * кол_во_месяцев))) * 100
        # Пример для 3 месяцев: (1 - (429 / (149 * 3))) * 100 = 4%
        discount = int((1 - (current_price / (base_price_30 * month_count))) * 100)

        discount_str = f" (-{discount}%)" if discount > 0 else ""

        builder.row(InlineKeyboardButton(
            text=f"{text} - {current_price} ₽{discount_str}",
            callback_data=f"ch_{tariff}_{days}"
        ))

    builder.row(InlineKeyboardButton(text="⤿ Назад", callback_data="menu_sub"))
    return builder.as_markup()

@router.callback_query(F.data.startswith("ch_"))
async def ch_sub(callback: CallbackQuery):
    await callback.answer()
    tariff = callback.data.split("_")[1]
    days = callback.data.split("_")[2]

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Оплатить", callback_data=f"nt_{tariff}_{days}"))
    builder.row(InlineKeyboardButton(text="⤿ Назад", callback_data=f"change_sub_{tariff}"))

    await callback.message.edit_text(
        text=f"Изменение подписки на {tariff} - {days} дней?\n"
             f"Цена: {PRICES[tariff][days]} ₽",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("nt_"))
async def extend_sub_pay(callback: CallbackQuery):
    await callback.answer()
    id_user = callback.from_user.id
    parts = callback.data.split("_")
    tariff, day = parts[1], int(parts[2])
    if MANUAL_PAYMENT:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Я оплатил", callback_data=f"PAY_CHANGE_{tariff}_{day}"))
        builder.row(InlineKeyboardButton(text="⤿ Назад", callback_data=f"ch_{tariff}_{day}"))

        await callback.message.edit_text(
            f"ТУТ ДОЛЖНЫ БЫТЬ РЕКВИЗИТЫ\n"
            f"\n"
            f"Изменение подписки на {tariff} - {day} дней.\n"
            f"К оплате: {PRICES.get(tariff, {}).get(str(day))} ₽",
            reply_markup=builder.as_markup()
        )
    else:
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass
        await create_payment(callback.bot, id_user, tariff, day)  # создание платежа

@router.callback_query(F.data.startswith("PAY_CHANGE_"))
async def pay_extended(callback: CallbackQuery):
    await callback.answer()
    tariff = callback.data.split("_")[2]
    days = callback.data.split("_")[3]
    user_id = callback.from_user.id
    user_name = f"tg_{user_id}"
    user_info = await marzban_api.get_user_info(user_name)
    db_check = await check_order(user_id, 'update')
    if db_check:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Главное меню", callback_data='start'))
        await callback.message.edit_text("Подождите пока администратор подтвердит оплату!", reply_markup=builder.as_markup())
        return
    if user_info:
        await add_expire_order(user_id, tariff, days, "update")
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Главное меню", callback_data='start'))
        await callback.message.edit_text("Платеж принят в обработку, в скором времени ваша подписка станет активной!", reply_markup=builder.as_markup())
        await callback.bot.send_message(text=f"Пользователь {user_id} изменил подписку на {tariff} - {days} дней.", chat_id=ADMIN_ID)

@router.callback_query(F.data == 'get_link')
async def get_lik(callback: CallbackQuery):
    await callback.answer()
    user_name = f'tg_{callback.from_user.id}'
    user_data = await marzban_api.get_user_info(user_name)
    sub_link = user_data.get('subscription_url')
    if sub_link:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Копировать ссылку", copy_text=CopyTextButton(text=sub_link)))
        builder.row(InlineKeyboardButton(text="Как подключиться?", callback_data='instruction'))
        builder.row(InlineKeyboardButton(text="⤿ Назад", callback_data='menu_sub'))

        await callback.message.edit_text(text=f"Ваша ссылка для подключения 👇\n"
                                              f"(нажмите на нее, что бы скопировать)\n"
                                              f"\n"
                                              f"<code>{sub_link}</code>",
                                         parse_mode='HTML',
                                         reply_markup=builder.as_markup())
from aiogram import Router, F
from aiogram.types import InlineKeyboardButton, CallbackQuery, CopyTextButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.marzban import marzban_api
from services.utils import days_left, traffic_left, SUB_STATUS
from prices import PRICES
from utils.keyboards import get_sub_menu_kb
from utils.text import NO_SUB_TEXT, SUB_MENU_MAIN_TEXT

router = Router()

@router.callback_query(F.data == 'menu_sub')
async def menu_sub(callback: CallbackQuery):
    await callback.answer()
    tg_id = callback.from_user.id
    user_id = f"tg_{tg_id}"
    user_info = await marzban_api.get_user_info(user_id)
    if not user_info:
        await callback.message.edit_text(text=NO_SUB_TEXT,
                                         eply_markup=get_no_sub_menu())
        return
    tariff = user_info.get('note')
    expire = user_info.get("expire")

    if not expire:  # None или 0
        days = '∞'
    else:
        days = max(0, days_left(expire))

    traffic = traffic_left(user_info["data_limit"], user_info['used_traffic'])
    status = user_info.get('status')
    sub_status = SUB_STATUS.get(status, None)

    await callback.message.edit_text(text=SUB_MENU_MAIN_TEXT.format(user_info=tariff,
                                                                    tg_id=tg_id,
                                                                    sub_status=sub_status,
                                                                    days=days,
                                                                    traffic=traffic),
                                     reply_markup=get_sub_menu_kb(tariff),
                                     parse_mode="html")

def get_no_sub_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Купить VPN", callback_data='vpn_start'))
    builder.row(InlineKeyboardButton(text="⤿ Назад", callback_data='start'))
    return builder.as_markup()


@router.callback_query(F.data == 'add_days')
async def add_days(callback: CallbackQuery):
    await callback.answer()
    tg_id = callback.from_user.id
    user_name = f"tg_{tg_id}"
    user_info = await marzban_api.get_user_info(user_name)

    if not user_info:
        await callback.message.edit_text("У вас нет активной подписки!", reply_markup=get_no_sub_menu())
        return

    tariff = user_info['note']
    await callback.message.edit_text(
        text=f'Выберите на сколько требуется продлить подписку {tariff}',
        reply_markup=tariff_menu('extend',tariff)
    )

@router.callback_query(F.data.startswith("extend_"))
async def extend_sub(callback: CallbackQuery):
    await callback.answer()
    tariff = callback.data.split("_")[1]
    days = callback.data.split("_")[2]

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Оплатить", callback_data=f"pay_{tariff}_{days}"))
    builder.row(InlineKeyboardButton(text="⤿ Назад", callback_data="add_days"))

    await callback.message.edit_text(
        text=f"Продлить подписку {tariff} на {days} дней?\n"
             f"Цена: {PRICES[tariff][days]} ₽",
        reply_markup=builder.as_markup()

    )

@router.callback_query(F.data == 'new_tariff')
async def new_tariff(callback: CallbackQuery):
    await callback.answer()
    user_id = f"tg_{callback.from_user.id}"
    user_info = await marzban_api.get_user_info(user_id)

    if user_info.get('status') != 'expired' and user_info.get('note') != 'TRIAL':
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
    await callback.message.edit_text(text=f"Выберите срок подписки {tariff}", reply_markup=tariff_menu("ch",tariff))

def tariff_menu(prefix, tariff):
    tariff = str(tariff)
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
        discount = int((1 - (current_price / (base_price_30 * month_count))) * 100)
        discount_str = f" (-{discount}%)" if discount > 0 else ""
        builder.row(InlineKeyboardButton(
            text=f"{text} - {current_price} ₽{discount_str}",
            callback_data=f"{prefix}_{tariff}_{days}"
        ))

    builder.row(InlineKeyboardButton(text="⤿ Назад", callback_data="menu_sub"))
    return builder.as_markup()

@router.callback_query(F.data.startswith("ch_"))
async def ch_sub(callback: CallbackQuery):
    await callback.answer()
    tariff = callback.data.split("_")[1]
    days = callback.data.split("_")[2]

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Оплатить", callback_data=f"pay_{tariff}_{days}"))
    builder.row(InlineKeyboardButton(text="⤿ Назад", callback_data=f"change_sub_{tariff}"))

    await callback.message.edit_text(
        text=f"Изменить подписку {tariff} - {days} дней?\n"
             f"\n"
             f"Цена: {PRICES[tariff][days]} ₽",
        reply_markup=builder.as_markup()
    )

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
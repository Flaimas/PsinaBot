from aiogram.types import CopyTextButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from config import SUPPORT_URL
from prices import PRICES


def get_trial_tech_error_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data='start'))
    builder.row(InlineKeyboardButton(text="Помощь", callback_data='help'))
    return builder.as_markup()

def get_trial_error_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💳 Приобрести подписку", callback_data='tariff_menu'))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data='start'))
    return builder.as_markup()

def get_trial_success_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔗 Получить ссылку", callback_data='get_link'))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data='start'))
    return builder.as_markup()

def get_menu_trial_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Активировать пробную подписку", callback_data='trial_subscription'))
    builder.row(InlineKeyboardButton(text="Главное меню", callback_data='start'))
    return builder.as_markup()

def get_start_kb(sub_status):
    builder = InlineKeyboardBuilder()

    if sub_status:
        builder.row(InlineKeyboardButton(text="Управление подпиской", callback_data=f"menu_sub"))
    if not sub_status:
        builder.row(InlineKeyboardButton(text="Пробная подписка", callback_data=f"menu_trial"))
        builder.row(InlineKeyboardButton(text="Купить VPN", callback_data=f"tariff_menu"))

    builder.row(InlineKeyboardButton(text="Инструкции", callback_data="instruction"), InlineKeyboardButton(text="Рефералы", callback_data='referral'))
    builder.row(InlineKeyboardButton(text="Помощь", callback_data="help"))
    return builder.as_markup()

def get_referral_kb(link):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Поделиться с другом",
                                     switch_inline_query=f"\nПользуюсь этим VPN, держи ссылку: {link}" ))
    builder.row(InlineKeyboardButton(text="Главное меню", callback_data='start'))
    return builder.as_markup()

def get_success_payment_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Управление подпиской", callback_data='menu_sub'))
    builder.row(InlineKeyboardButton(text="Главное меню", callback_data='start'))
    return builder.as_markup()

def get_failed_payment_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Поддержка", callback_data='help'))
    return builder.as_markup()

def get_add_reward_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Посмотреть", callback_data='referral'))
    return builder.as_markup()

def get_new_user_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Получить подарок", callback_data='trial_subscription'))
    builder.row(InlineKeyboardButton(text="Главное меню", callback_data='start'))
    return builder.as_markup()

def get_create_payment_kb(payment_url: str, tariff: str):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Оплатить и подключиться 💳', url=payment_url))
    builder.row(InlineKeyboardButton(text='Выбрать период', callback_data=f"period_{tariff}"))
    builder.row(InlineKeyboardButton(text='Главное меню', callback_data=f'start'))
    return builder.as_markup()

def get_create_payment_error_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Главное меню', callback_data='start'))
    return builder.as_markup()

def get_sub_menu_kb(tariff):
    builder = InlineKeyboardBuilder()

    if tariff == 'TRIAL':
        builder.row(InlineKeyboardButton(text="Изменить тариф", callback_data='tariff_menu'))
    else:
        builder.row(InlineKeyboardButton(text="Продлить подписку", callback_data=f'period_{tariff}'),
                    InlineKeyboardButton(text="Изменить тариф", callback_data='tariff_menu'))

    builder.row(InlineKeyboardButton(text="Получить ссылку", callback_data='get_link'))
    builder.row(InlineKeyboardButton(text="Главное меню", callback_data='start'))
    return builder.as_markup()

def get_no_sub_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Купить VPN", callback_data='tariff_menu'))
    builder.row(InlineKeyboardButton(text="⤿ Назад", callback_data='start'))
    return builder.as_markup()

def get_tariff_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="STANDART (до 3 устройств) - трафик 200 гб", callback_data='period_STANDART'))
    builder.row(InlineKeyboardButton(text="GO (до 5 устройств) - трафик 400 гб", callback_data='period_GO'))
    builder.row(InlineKeyboardButton(text="PRO (до 9 устройств) - трафик 800 гб", callback_data='period_PRO'))
    builder.row(InlineKeyboardButton(text="Вернуться в меню", callback_data='start'))
    return builder.as_markup()

def get_link_kb(sub_link):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Копировать ссылку", copy_text=CopyTextButton(text=sub_link)))
    builder.row(InlineKeyboardButton(text="Как подключиться?", callback_data='instruction'))
    builder.row(InlineKeyboardButton(text="⤿ Назад", callback_data='menu_sub'))
    return builder.as_markup()

def get_period_menu_kb(tariff: str):
    builder = InlineKeyboardBuilder()
    periods = PRICES.get(tariff)
    builder.row(InlineKeyboardButton(text=f'1  месяц   — {periods.get('30')}₽',callback_data=f'pay_{tariff}_30'))
    builder.row(InlineKeyboardButton(text=f'2  месяца  — {periods.get('60')}₽',callback_data=f'pay_{tariff}_60'))
    builder.row(InlineKeyboardButton(text=f'6  месяцев — {periods.get('180')}₽',callback_data=f'pay_{tariff}_180'))
    builder.row(InlineKeyboardButton(text=f'12 месяцев — {periods.get('360')}₽',callback_data=f'pay_{tariff}_360'))
    builder.row(InlineKeyboardButton(text=f'Вернуться в тарифы', callback_data='tariff_menu'))
    builder.row(InlineKeyboardButton(text=f'Вернуться в меню', callback_data='start'))
    return builder.as_markup()

def get_tariff_menu_existing_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Назад", callback_data='menu_sub'))
    builder.row(InlineKeyboardButton(text="Главное меню", callback_data='start'))
    return builder.as_markup()

def get_help_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Инструкции", callback_data='instruction'))
    builder.row(InlineKeyboardButton(text="Поддержка", url=SUPPORT_URL))
    builder.row(InlineKeyboardButton(text="Главное меню", callback_data='start'))
    return builder.as_markup()

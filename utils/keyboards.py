from aiogram.types import CopyTextButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from config import SUPPORT_URL
from prices import PRICES

def get_trial_tech_error_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data='start'))
    builder.row(InlineKeyboardButton(text="Техподдержка", url=SUPPORT_URL))
    return builder.as_markup()

def get_trial_error_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💳 Купить подписку", callback_data='tariff_menu'))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data='start'))
    return builder.as_markup()

def get_trial_success_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔗 Получить подписку", callback_data='get_link'))
    builder.row(InlineKeyboardButton(text="Инструкции", callback_data='instruction'))
    return builder.as_markup()

def get_menu_trial_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Активировать период", callback_data='trial_subscription'))
    builder.row(InlineKeyboardButton(text="Назад", callback_data='start'))
    return builder.as_markup()

def get_start_kb(sub_status):
    builder = InlineKeyboardBuilder()
    if sub_status:
        builder.row(InlineKeyboardButton(text="💎 Управление подпиской", callback_data="menu_sub"))
    else:
        builder.row(InlineKeyboardButton(text="🎁 Пробный период", callback_data="menu_trial"))
        builder.row(InlineKeyboardButton(text="💳 Купить VPN", callback_data="tariff_menu"))

    builder.row(
        InlineKeyboardButton(text="Инструкции", callback_data="instruction"),
        InlineKeyboardButton(text="Рефералы", callback_data='referral')
    )
    builder.row(InlineKeyboardButton(text="Техподдержка", callback_data="help"))
    return builder.as_markup()

def get_referral_kb(link):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Поделиться ссылкой",
                                     switch_inline_query=f"\nПользуюсь этим VPN, держи ссылку: {link}"))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data='start'))
    return builder.as_markup()

def get_success_payment_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Настроить подключение", callback_data='menu_sub'))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data='start'))
    return builder.as_markup()

def get_failed_payment_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Связаться с поддержкой", url=SUPPORT_URL))
    builder.row(InlineKeyboardButton(text="Попробовать снова", callback_data='tariff_menu'))
    return builder.as_markup()

def get_add_reward_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Мои рефералы", callback_data='referral'))
    return builder.as_markup()

def get_new_user_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Забрать бонус", callback_data='trial_subscription'))
    builder.row(InlineKeyboardButton(text="В меню", callback_data='start'))
    return builder.as_markup()

def get_create_payment_kb(payment_url: str, tariff: str, payment_id: str):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Оплатить подписку 💳', url=payment_url))
    builder.row(InlineKeyboardButton(text='Проверить оплату', callback_data=f'check_payment_{payment_id}'))
    builder.row(InlineKeyboardButton(text='Изменить срок', callback_data=f"period_{tariff}"))
    builder.row(InlineKeyboardButton(text='Отмена', callback_data=f'start'))
    return builder.as_markup()

def get_create_payment_error_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Повторить попытку', callback_data='tariff_menu'))
    builder.row(InlineKeyboardButton(text='🏠 Главное меню', callback_data='start'))
    return builder.as_markup()

def get_sub_menu_kb(tariff):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔗 Получить подписку", callback_data='get_link'))

    if tariff == 'TRIAL':
        builder.row(InlineKeyboardButton(text="Выбрать основной тариф", callback_data='tariff_menu'))
    else:
        builder.row(
            InlineKeyboardButton(text="Продлить", callback_data=f'period_{tariff}'),
            InlineKeyboardButton(text="Сменить тариф", callback_data='tariff_menu')
        )
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data='start'))
    return builder.as_markup()


def get_no_sub_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Выбрать тариф", callback_data='tariff_menu'))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data='start'))
    return builder.as_markup()


def get_tariff_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="STANDART — Базовый", callback_data='period_STANDART'))
    builder.row(InlineKeyboardButton(text="GO — Оптимальный", callback_data='period_GO'))
    builder.row(InlineKeyboardButton(text="PRO — Максимальный", callback_data='period_PRO'))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data='start'))
    return builder.as_markup()


def get_link_kb(sub_link):
    builder = InlineKeyboardBuilder()
    # Используем CopyTextButton для современных версий aiogram
    builder.row(InlineKeyboardButton(text="📋 Копировать ссылку", copy_text=CopyTextButton(text=sub_link)))
    builder.row(InlineKeyboardButton(text="Инструкция по настройке", callback_data='instruction'))
    builder.row(InlineKeyboardButton(text="Назад", callback_data='menu_sub'))
    return builder.as_markup()


def get_period_menu_kb(tariff: str):
    builder = InlineKeyboardBuilder()
    periods = PRICES.get(tariff)
    builder.row(InlineKeyboardButton(text=f"1 месяц — {periods.get('30')}₽", callback_data=f'pay_{tariff}_30'))
    builder.row(InlineKeyboardButton(text=f"2 месяца — {periods.get('60')}₽", callback_data=f'pay_{tariff}_60'))
    builder.row(InlineKeyboardButton(text=f"6 месяцев — {periods.get('180')}₽", callback_data=f'pay_{tariff}_180'))
    builder.row(InlineKeyboardButton(text=f"12 месяцев — {periods.get('360')}₽", callback_data=f'pay_{tariff}_360'))
    builder.row(InlineKeyboardButton(text="Назад к тарифам", callback_data='tariff_menu'))
    return builder.as_markup()

def get_tariff_menu_existing_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Назад к подписке", callback_data='menu_sub'))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data='start'))
    return builder.as_markup()

def get_help_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Инструкции по настройке", callback_data='instruction'))
    builder.row(InlineKeyboardButton(text="Написать в поддержку", url=SUPPORT_URL))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data='start'))
    return builder.as_markup()

def get_instructions_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="iOS / iPhone", callback_data='ios'),
        InlineKeyboardButton(text="Android", callback_data='android')
    )
    builder.row(
        InlineKeyboardButton(text="Windows", callback_data='windows'),
        InlineKeyboardButton(text="macOS", callback_data='mac_os')
    )
    builder.row(InlineKeyboardButton(text="Android TV", callback_data='android_tv'))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data='start'))
    return builder.as_markup()

def get_app_install_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔗 Получить подписку", callback_data='get_link'))
    builder.row(
        InlineKeyboardButton(text="« Назад", callback_data="instruction"),
        InlineKeyboardButton(text="🏠 В меню", callback_data="start")
    )
    return builder.as_markup()

def get_admin_panel_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Подписка на сутки", callback_data='tg_access'), InlineKeyboardButton(text="Логи", callback_data='logs'))
    builder.row(InlineKeyboardButton(text="Главное меню", callback_data='start'))
    return builder.as_markup()

def get_tg_access_kb(access_link):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Скопировать", copy_text=CopyTextButton(text=access_link)))
    builder.row(InlineKeyboardButton(text="Главное меню", callback_data='start'))
    builder.row(InlineKeyboardButton(text="Назад", callback_data='admin'))
    return builder.as_markup()

def get_notification_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Админ-панель", callback_data='admin'))
    return builder.as_markup()
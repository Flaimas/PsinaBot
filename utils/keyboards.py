from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

def get_trial_tech_error_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data='start'))
    builder.row(InlineKeyboardButton(text="Помощь", callback_data='help'))
    return builder.as_markup()

def get_trial_error_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💳 Приобрести подписку", callback_data='vpn_start'))
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
        builder.row(InlineKeyboardButton(text="Пробная подписка на 3 дня", callback_data=f"menu_trial"))
        builder.row(InlineKeyboardButton(text="Купить VPN", callback_data=f"vpn_start"))

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
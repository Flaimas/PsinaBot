MENU_IMAGES = {
    'start': 'AgACAgIAAxkBAAIGGGnWOgn0K1wlzRxdM41Z6TeWkX6ZAAItFWsbuXSwSjl5Q2kc7ln6AQADAgADeQADOwQ',
    'error': 'AgACAgIAAxkBAAIF-GnPtaD0HA_Yw5x7f_hPPDqROv5RAAL8GWsbBWNxSuqwGIr3wJp6AQADAgADeQADOgQ',
    'trial_sub': 'AgACAgIAAxkBAAIF-GnPtaD0HA_Yw5x7f_hPPDqROv5RAAL8GWsbBWNxSuqwGIr3wJp6AQADAgADeQADOgQ',
    'sub_menu': 'AgACAgIAAxkBAAIGHWnWOkwBQTBi07Di9MRH_WYnMaJFAAIyFWsbuXSwSpB-xDccbBLtAQADAgADeQADOwQ',
    'link_menu': 'AgACAgIAAxkBAAIF-GnPtaD0HA_Yw5x7f_hPPDqROv5RAAL8GWsbBWNxSuqwGIr3wJp6AQADAgADeQADOgQ',
    'menu_trial': 'AgACAgIAAxkBAAIF-GnPtaD0HA_Yw5x7f_hPPDqROv5RAAL8GWsbBWNxSuqwGIr3wJp6AQADAgADeQADOgQ',
    'ref_menu': 'AgACAgIAAxkBAAIF-GnPtaD0HA_Yw5x7f_hPPDqROv5RAAL8GWsbBWNxSuqwGIr3wJp6AQADAgADeQADOgQ',
    'help_menu': 'AgACAgIAAxkBAAIF-GnPtaD0HA_Yw5x7f_hPPDqROv5RAAL8GWsbBWNxSuqwGIr3wJp6AQADAgADeQADOgQ',
    'instructions_menu': 'AgACAgIAAxkBAAIF-GnPtaD0HA_Yw5x7f_hPPDqROv5RAAL8GWsbBWNxSuqwGIr3wJp6AQADAgADeQADOgQ',
    'pay_menu': 'AgACAgIAAxkBAAIF-GnPtaD0HA_Yw5x7f_hPPDqROv5RAAL8GWsbBWNxSuqwGIr3wJp6AQADAgADeQADOgQ',
    'error_pay': 'AgACAgIAAxkBAAIF-GnPtaD0HA_Yw5x7f_hPPDqROv5RAAL8GWsbBWNxSuqwGIr3wJp6AQADAgADeQADOgQ',
    'tariff_menu': 'AgACAgIAAxkBAAIF-GnPtaD0HA_Yw5x7f_hPPDqROv5RAAL8GWsbBWNxSuqwGIr3wJp6AQADAgADeQADOgQ',
}

TEXT_START_MENU = (
    "Привет, {user_name}!\n"
    "<blockquote>Ваш ID: <code>{user_id}</code>\n"
    "Статус подписки: {icon_status}</blockquote>"
)

TRIAL_ERROR_TEXT = (
    "<b>Ошибка</b>\n\n"
    "Вы уже использовали пробный период.\n"
    "Приобрести подписку можно в личном кабинете."
)

TRIAL_SUCCESS_TEXT = (
    "<b>Готово!</b>\n\n"
    "Пробный период активирован. Настройте подключение по инструкции в главном меню.\n"
    "После окончания срока вы сможете продлить доступ в личном кабинете."
)

ERROR_TECH_TEXT = "Техническая ошибка. Пожалуйста, повторите попытку позже."

MENU_TRIAL_TEXT = (
    "Активируйте пробный период, чтобы протестировать скорость и стабильность соединения.\n\n"
    "Доступ закроется автоматически по истечении срока."
)

NEW_USER_TEXT = (
    "Вы присоединились по приглашению: <code>{referrer_id}</code>\n\n"
    "Вам начислено 7 дополнительных дней к пробному периоду."
)

REFERRAL_HANDLER_TEXT = (
    "<b>Реферальная система</b>\n\n"
    "Приглашайте друзей и получайте бонусы на баланс для оплаты подписки.\n\n"
    "Приглашено друзей: {count_ref}\n"
    "Заработано всего: {reward_balance} ₽\n\n"
    "<b>Ваша ссылка для приглашения:</b>\n"
    "<code>{link}</code>"
)

CREATE_PAYMENT_TEXT = (
    "<b>Подтверждение заказа</b>\n\n"
    "Тариф: {tariff}\n"
    "Срок: {day} дней\n"
    "К оплате: {amount} ₽\n\n"
    "<b>Внимание:</b>\n"
    "— Перед оплатой обязательно отключите действующий VPN\n"
    "— После совершения платежа не закрывайте это окно до подтверждения активации"
)

CREATE_PAYMENT_ERROR_TEXT = (
    "Ошибка платежного шлюза.\n"
    "Сервис оплаты временно недоступен, попробуйте через несколько минут."
)

PAYMENT_SUCCESS_TEXT = "Тариф {tariff} успешно активирован. Срок продлен на {day} дней."

PAYMENT_FAILED_TEXT = "Ошибка синхронизации с VPN-сервером. Пожалуйста, обратитесь в поддержку."

ADD_REWARD_TEXT = "💰 Начисление: ваш реферал оформил подписку. Вам зачислено {reward_amount} ₽"

NO_SUB_TEXT = (
    "Активная подписка не найдена.\n"
    "Для возобновления доступа выберите тариф ниже."
)

SUB_MENU_MAIN_TEXT = (
    "<b>Управление подпиской</b>\n\n"
    "<blockquote>ID: <code>{tg_id}</code>\n"
    "Тариф: {user_info}\n"
    "Статус: {sub_status}\n"
    "Осталось дней: {days}\n"
    "Израсходованный трафик: {traffic}</blockquote>"
)

SUB_LIST_TEXT = (
    "<b>Доступные тарифы</b>\n\n"
    "<blockquote><b>STANDART</b>\nБазовый доступ для личного пользования.\nДо 3 устройств, 200 ГБ трафика.\n\n"
    "<b>GO</b>\nОптимально для активного серфинга и видео.\nДо 5 устройств, 400 ГБ трафика.\n\n"
    "<b>PRO</b>\nМаксимальная скорость без ограничений.\nДо 9 устройств, 800 ГБ трафика.</blockquote>"
)

PERIOD_MENU_TEXT = (
    "<b>Выбор периода</b>\n\n"
    "Выберите срок действия подписки.\n"
    "При оплате на длительный срок действует прогрессивная скидка."
)

EXISTING_TARIFF_TEXT = (
    "<b>У вас уже есть активный тариф</b>\n\n"
    "Изменение условий или продление будет доступно после завершения текущего срока."
)

GET_LINK_TEXT = (
    "<b>Ваша ссылка для подключения:</b>\n\n"
    "<code>{sub_link}</code>\n\n"
    "Нажмите на ссылку, чтобы скопировать её в буфер обмена."
)

HELP_TEXT = (
    "<b>Техническая поддержка</b>\n\n"
    "Ваш ID: <code>{id_user}</code> (нажмите, чтобы скопировать)\n\n"
    "Если у вас возникли проблемы с настройкой, изучите инструкции в нашей базе знаний.\n\n"
    "Специалисты поддержки на связи с 10:00 до 20:00 по МСК."
)

INSTRUCTION_HANDLER_TEXT = (
    "<b>Инструкции по настройке</b>\n\n"
    "Выберите вашу операционную систему для получения пошагового руководства:"
)
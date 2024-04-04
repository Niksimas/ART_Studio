from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.settings import settings


def admin_menu(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="users")],
        [InlineKeyboardButton(text="💬 Изменить стартовое сообщение", callback_data="edit_start_mess")],
        [InlineKeyboardButton(text="🔁 Сменить чат администраторов", callback_data="new_chat")],
        [InlineKeyboardButton(text="Добавить услугу", callback_data="add_service")],
    ]
    if user_id == settings.bots.admin_id:
        buttons.append([InlineKeyboardButton(text="Добавить админа", callback_data="add_admin"),
                        InlineKeyboardButton(text="Удалить админа", callback_data="del_admin")])
    buttons.append([InlineKeyboardButton(text="В меню", callback_data="start")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def confirmation(txt_y: str = "🟢 Да", txt_n: str = "🔴 Нет", cd_y: str = "yes", cd_n: str = "no", canc_data: str = "start"):
    buttons = [
        [
            InlineKeyboardButton(text=txt_y, callback_data=cd_y),
            InlineKeyboardButton(text=txt_n, callback_data=cd_n)
        ],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data=canc_data)]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def cancel_admin(calldata_return: str = "admin"):
    buttons = [[InlineKeyboardButton(text="↩️ Вернуться", callback_data=calldata_return)]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def del_admin(admins: dict):
    buttons = []
    for i in admins.keys():
        buttons.append([InlineKeyboardButton(text=admins[i], callback_data=f"del_{i}")])
    buttons.append([InlineKeyboardButton(text="↩️ Вернуться", callback_data="start")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def custom_btn(text: str, cldata: str):
    buttons = [[InlineKeyboardButton(text=text, callback_data=cldata)]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def edit_btn_with_photo(type_mess: str, callback_data: str = "start"):
    buttons = [
        [InlineKeyboardButton(text="🖼 Фотография", callback_data=f"edit_photo_{type_mess}")],
        [InlineKeyboardButton(text="🔤 Текст", callback_data=f"edit_text_{type_mess}")],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data=callback_data)]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def edit_btn_with_text(type_mess: str, callback_data: str = "start"):
    buttons = [
        [InlineKeyboardButton(text="🔤 Текст", callback_data=f"edit_text_{type_mess}")],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data=callback_data)]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def edit_btn_for_contact():
    buttons = [
        [InlineKeyboardButton(text="🔤 Текст", callback_data=f"edit_text_contact")],
        [InlineKeyboardButton(text="🔤 Текст кнопки", callback_data=f"edit_btn_text_watsapp")],
        [InlineKeyboardButton(text="🔤 Ссылку кнопки", callback_data=f"edit_btn_link_watsapp")],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data="contacts")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def edit_btn_for_social_network(btn1: str, btn2: str, btn3: str, btn4: str):
    buttons = [
        [
            InlineKeyboardButton(text="🔤 Текст 1 кнопки", callback_data=f"edit_btn_text_{btn1}"),
            InlineKeyboardButton(text="🔤 Ссылку 1 кнопки", callback_data=f"edit_btn_link_{btn1}")
        ],
        [
            InlineKeyboardButton(text="🔤 Текст 2 кнопки", callback_data=f"edit_btn_text_{btn2}"),
            InlineKeyboardButton(text="🔤 Ссылку 2 кнопки", callback_data=f"edit_btn_link_{btn2}")
        ],
        [
            InlineKeyboardButton(text="🔤 Текст 3 кнопки", callback_data=f"edit_btn_text_{btn3}"),
            InlineKeyboardButton(text="🔤 Ссылку 3 кнопки", callback_data=f"edit_btn_link_{btn3}")
        ],
        [
            InlineKeyboardButton(text="🔤 Текст 4 кнопки", callback_data=f"edit_btn_text_{btn4}"),
            InlineKeyboardButton(text="🔤 Ссылку 4 кнопки", callback_data=f"edit_btn_link_{btn4}")
        ],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data="social_network")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def edit_service(type_mess: str):
    buttons = [
        [InlineKeyboardButton(text="🖼 Фотография", callback_data=f"edit_s_photo_{type_mess}")],
        [InlineKeyboardButton(text="🔤 Название", callback_data=f"edit_s_name_{type_mess}")],
        [InlineKeyboardButton(text="🔤 Описание", callback_data=f"edit_s_text_{type_mess}")],
        [InlineKeyboardButton(text="🔤 Стоимость", callback_data=f"edit_s_amount_{type_mess}")],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data="service_" + type_mess)]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def choice_amount_id(data: list):
    buttons = []
    for i in range(len(data)):
        buttons.append([InlineKeyboardButton(text=data[i]["name_amount"] + ": " + str(data[i]["amount"]),
                                             callback_data=f"amount_{data[i]['id']}")])
    buttons.append([InlineKeyboardButton(text="↩️ Вернуться", callback_data="services")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

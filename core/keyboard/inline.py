from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.database.database import get_all_id_admin


def start(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="ℹ️ О студии", callback_data="description"),
            InlineKeyboardButton(text="⭕️🛎 Наши услуги", callback_data="services")
        ],
        [InlineKeyboardButton(text="💠 Бонусы", callback_data="bonuses")],
        [InlineKeyboardButton(text="📱 Контактные данные", callback_data="contacts")],
        [InlineKeyboardButton(text="🌐 Мы в социальных сетях", callback_data="social_network")],
        [InlineKeyboardButton(text="📍 Где мы находимся", callback_data="address")],
        [InlineKeyboardButton(text="⏳ Часы работы", callback_data="working_hours")],
        [InlineKeyboardButton(text="❔ Задать вопрос", callback_data="question")],
    ]
    if user_id in (get_all_id_admin()):
        buttons.append([InlineKeyboardButton(text='⭐️ Администратору', callback_data="admin")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def to_return(name_service: str, user_id: int = None):
    """call_data: start"""
    buttons = [[InlineKeyboardButton(text="↩️ Вернуться", callback_data="start")]]
    if user_id in (get_all_id_admin()):
        buttons.append([InlineKeyboardButton(text='⭐️ Редактировать', callback_data=f"edit_{name_service}")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def url_btn(data: dict, user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=data["text"], url=data["link"])],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data="start")]
    ]
    if user_id in (get_all_id_admin()):
        buttons.append([InlineKeyboardButton(text='⭐️ Редактировать', callback_data="edit_contact")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def social_network_btn(data_VK: dict, data_TG: dict, data_Site: dict, data_inst: dict, user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=data_Site["text"], url=data_Site["link"])],
        [InlineKeyboardButton(text=data_TG["text"], url=data_TG["link"])],
        [InlineKeyboardButton(text=data_VK["text"], url=data_VK["link"])],
        [InlineKeyboardButton(text=data_inst["text"], url=data_inst["link"])],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data="start")]
    ]
    if user_id in (get_all_id_admin()):
        buttons.append([InlineKeyboardButton(text='⭐️ Редактировать', callback_data="edit_social_network")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def question_btn() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📱 Контактные данные", callback_data="contacts")],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data="start")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def check_up() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🟢 Да", callback_data="yes"),
            InlineKeyboardButton(text="🔴 Нет", callback_data="no")
        ],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data="start")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def menu_service():
    buttons = [
        [InlineKeyboardButton(text="⭕️Уроки по песочной анимации", callback_data="start")],
        [InlineKeyboardButton(text="⭕️Мастер-классы по рисованию акрилом", callback_data="start")],
        [
            InlineKeyboardButton(text="⭕️Курс юных леди ", callback_data="start"),
            InlineKeyboardButton(text="⭕️Курс юных джентльменов", callback_data="start")
        ],
        [InlineKeyboardButton(text="⭕️Выездные мастер-классы по рисованию", callback_data="start")],
        [InlineKeyboardButton(text="⭕️Мастер-классы по пошиву изделий из трикотажа", callback_data="start")],
        [InlineKeyboardButton(text="⭕️Мастер-класс по рисованию на спиле дерева", callback_data="start")],
        [InlineKeyboardButton(text="⭕️Съедобная мастерская", callback_data="start")],
        [InlineKeyboardButton(text="⭕️Дни Рождения", callback_data="start")],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data="start")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def state_cancel() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Отменить действие", callback_data="state_cancel"))
    return builder


def custom_btn(text: str, cldata: str):
    buttons = [[InlineKeyboardButton(text=text, callback_data=cldata)]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

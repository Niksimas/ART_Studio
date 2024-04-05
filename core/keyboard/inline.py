from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import datetime as dt

from core.database.database import get_all_id_admin, check_birthday, get_all_service


def start(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="ℹ️ О студии", callback_data="description"),
            InlineKeyboardButton(text="🛎 Наши услуги", callback_data="services")
        ],
        [InlineKeyboardButton(text="💠 Бонусы", callback_data="bonuses")],
        [InlineKeyboardButton(text="📱 Контактные данные", callback_data="contacts")],
        [InlineKeyboardButton(text="🌐 Мы в социальных сетях", callback_data="social_network")],
        [InlineKeyboardButton(text="📍 Где мы находимся", callback_data="address")],
        [InlineKeyboardButton(text="⏳ Часы работы", callback_data="working-hours")],
        [InlineKeyboardButton(text="❔ Задать вопрос", callback_data="question")],
    ]
    if user_id in (get_all_id_admin()):
        buttons.append([InlineKeyboardButton(text='⭐️ Администратору', callback_data="admin")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def to_return(name_service: str = None, user_id: int = None, callback_data: str = "start"):
    """call_data: start"""
    buttons = [[InlineKeyboardButton(text="↩️ Вернуться", callback_data=callback_data)]]
    if user_id in (get_all_id_admin()):
        buttons.append([InlineKeyboardButton(text='⭐️ Редактировать', callback_data=f"edit_{name_service}")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def to_bonuses(name_service: str = None, user_id: int = None):
    buttons = [[InlineKeyboardButton(text="↩️ Вернуться", callback_data="start")]]
    if not check_birthday(user_id):
        buttons.insert(0, [InlineKeyboardButton(text="Установить дату рождения", callback_data="set_birthdate")])
    if user_id in (get_all_id_admin()):
        buttons.append([InlineKeyboardButton(text='⭐️ Редактировать', callback_data=f"edit_{name_service}")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def return_service(name_service: str):
    """call_data: start"""
    buttons = [[InlineKeyboardButton(text="↩️ Вернуться", callback_data="service_" + name_service)]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def url_btn(data: dict, user_id: int, callback_data: str = "start") -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=data["text"], url=data["link"])],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data=callback_data)]
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


def check_up(calldata_ret: str = "start") -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🟢 Да", callback_data="yes"),
            InlineKeyboardButton(text="🔴 Нет", callback_data="no")
        ],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data=calldata_ret)]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def menu_services():
    data = get_all_service()
    buttons = [[InlineKeyboardButton(text=i['name'], callback_data=f"service_{i['id']}")] for i in data]
    buttons.append([InlineKeyboardButton(text="↩️ Вернуться", callback_data="start")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def state_cancel() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Отменить действие", callback_data="state_cancel"))
    return builder


def menu_service(type_service: str, user_id: int):
    buttons = [
        [InlineKeyboardButton(text="✍️ Стоимость услуги", callback_data=f"amounts_{type_service}")],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data="services")],
    ]
    if user_id in (get_all_id_admin()):
        buttons.append([InlineKeyboardButton(text='⭐️ Редактировать', callback_data=f"edit_service_{type_service}"),
                        InlineKeyboardButton(text='⭐️ Удалить', callback_data=f"delserv_{type_service}")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def menu_service_send(type_service: str, user_id: int):
    buttons = [
        [InlineKeyboardButton(text="✍️ Записаться", callback_data=f"registration_{type_service}")],
        [InlineKeyboardButton(text="✍️ Стоимость услуги", callback_data=f"amounts_{type_service}")],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data="services")],
    ]
    if user_id in (get_all_id_admin()):
        buttons.append([InlineKeyboardButton(text='⭐️ Редактировать', callback_data=f"edit_service_{type_service}"),
                        InlineKeyboardButton(text='⭐️ Удалить', callback_data=f"delserv_{type_service}")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def custom_btn(text: str, cldata: str):
    buttons = [[InlineKeyboardButton(text=text, callback_data=cldata)]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def choice_amount(data: list):
    buttons = []
    for i in range(len(data)):
        buttons.append([InlineKeyboardButton(text=data[i]["name_amount"] + ": " + str(data[i]["amount"]),
                                             callback_data=f"amount_{data[i]['id']}")])
    buttons.append([InlineKeyboardButton(text="↩️ Вернуться", callback_data="services")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def url_btn_amount(data: dict, user_id: int, type_service: str, callback_data: str = "start") -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=data["text"], url=data["link"])],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data=callback_data)]
    ]
    if user_id in (get_all_id_admin()):
        buttons.append([InlineKeyboardButton(text='⭐️ Редактировать', callback_data=f"edit_s_amount_{type_service}")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


########################################################################################################################
# ##################################### строим календарик ############################################################ #
########################################################################################################################
def creat_list_calendar(in_data: dt.date, all_day: bool) -> dict:
    today = dt.date.today()
    if dt.datetime.now().weekday() in [0, 2, 4]:
        if dt.datetime.now().hour >= 11:
            today = dt.date.today() + dt.timedelta(days=1)
    else:
        if dt.datetime.now().hour >= 19:
            today = dt.date.today() + dt.timedelta(days=1)
    stop_day = today + dt.timedelta(days=32)
    result = {"days": [
                  "-", "-", "-", "-", "-", "-", "-",
                  "-", "-", "-", "-", "-", "-", "-",
                  "-", "-", "-", "-", "-", "-", "-",
                  "-", "-", "-", "-", "-", "-", "-",
                  "-", "-", "-", "-", "-", "-", "-"
              ],
              "back": "✖️✖️✖️",
              "next": "✖️✖️✖️"
              }
    day_start_month = dt.date(in_data.year, in_data.month, 1).weekday()
    k = 0
    for i in range(day_start_month, len(result["days"])):
        try:
            day = dt.date(in_data.year, in_data.month, k+1)
            k += 1
            if today <= day and day < stop_day:
                if not all_day and day.weekday() not in [1, 3]:
                    continue
                if all_day and day.weekday() in [5, 6]:
                    continue
                result["days"][i] = str(k)
        except ValueError:
            continue
    stop_day = dt.date(stop_day.year, stop_day.month, 1)
    if in_data >= stop_day:
        result["back"] = "<<<"
    if in_data < stop_day:
        result["next"] = ">>>"
    return result


def adding_month(input_date: dt.date) -> dt.date:
    try:
        new_data = dt.date(input_date.year, input_date.month+1, 1)
    except ValueError:
        new_data = dt.date(input_date.year+1, 1, 1)
    return new_data


def subtracting_month(input_date: dt.date) -> dt.date:
    try:
        new_data = dt.date(input_date.year, input_date.month-1, 1)
    except ValueError:
        new_data = dt.date(input_date.year-1, 12, 1)
    return new_data


def kalendar(in_data: dt.date, all_day: bool, cancel_cd: str = "start") -> InlineKeyboardMarkup:
    data_fun = creat_list_calendar(in_data, all_day)
    if in_data.month < 10:
        month = f"0{in_data.month}"
    else:
        month = in_data.month
    buttons = [
        [
            InlineKeyboardButton(text=f"{data_fun['back']}", callback_data=f"back-{in_data}"),
            InlineKeyboardButton(text=f"{month}.{in_data.year}", callback_data="month"),
            InlineKeyboardButton(text=f"{data_fun['next']}", callback_data=f"next-{in_data}")
        ],
        [InlineKeyboardButton(text=data_fun["days"][i],
                              callback_data=f"setd-{data_fun['days'][i]}-{in_data.month}-{in_data.year}")
         for i in range(0, 7)],
        [InlineKeyboardButton(text=data_fun["days"][i],
                              callback_data=f"setd-{data_fun['days'][i]}-{in_data.month}-{in_data.year}")
         for i in range(7, 14)],
        [InlineKeyboardButton(text=data_fun["days"][i],
                              callback_data=f"setd-{data_fun['days'][i]}-{in_data.month}-{in_data.year}")
         for i in range(14, 21)],
        [InlineKeyboardButton(text=data_fun["days"][i],
                              callback_data=f"setd-{data_fun['days'][i]}-{in_data.month}-{in_data.year}")
         for i in range(21, 28)],
        [InlineKeyboardButton(text=data_fun["days"][i],
                              callback_data=f"setd-{data_fun['days'][i]}-{in_data.month}-{in_data.year}")
         for i in range(28, 35)],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data=cancel_cd)]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def time_record(day: int, week_day: int, cancel_cd: str = "start"):
    if day == dt.date.today().day:
        time_now_hour = dt.datetime.now().hour
    else:
        time_now_hour = 0
    if week_day in [0, 2, 4]:
        buttons = [[InlineKeyboardButton(text="11:00 - 12:00", callback_data=f"time_11:00 - 12:00")]]
    else:
        if time_now_hour != 0:
            buttons = [[InlineKeyboardButton(text="19:00 - 20:00", callback_data=f"time_19:00 - 20:00")]]
        else:
            buttons = [
                [InlineKeyboardButton(text="14:00 - 15:00", callback_data=f"time_14:00 - 15:00")],
                [InlineKeyboardButton(text="19:00 - 20:00", callback_data=f"time_19:00 - 20:00")]
            ]
    buttons.append([InlineKeyboardButton(text="↩️ К датам", callback_data="back_time")])
    buttons.append([InlineKeyboardButton(text="↩️↩️ Вернуться", callback_data=cancel_cd)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def return_invoice(name_service: str):
    """call_data: start"""
    buttons = [
        [InlineKeyboardButton(text="Оплатить", pay=True)],
        [InlineKeyboardButton(text="↩️ Вернуться", callback_data="service_" + name_service)]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def share_number() -> ReplyKeyboardMarkup:
    button = [
        [KeyboardButton(text='Поделиться контактом', request_contact=True)],
        [KeyboardButton(text="Отмена")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=button, one_time_keyboard=True, resize_keyboard=True)
    return keyboard

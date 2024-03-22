import os

from decouple import config
from dataclasses import dataclass


import gspread
from gcsa.google_calendar import GoogleCalendar
from google.oauth2.service_account import Credentials


# Путь от корня системы до папки core например:
# D:\Programing\Flow_Work\core
home = os.path.dirname(__file__)


@dataclass
class Bots:
    bot_token: str
    admin_id: int
    chat_nil_id: int
    # admin_id_2: int


@dataclass
class Settings:
    bots: Bots
    link_sheet: str
    pay_token: str


def get_settings():
    return Settings(
        bots=Bots(
            bot_token=config("token"),
            admin_id=int(config("admin_id")),
            chat_nil_id=int(config("chat_nil_id"))
        ),
        link_sheet=config("sheet"),
        pay_token=config("pay_token")
    )


def get_admin_id():
    from core.database.database import get_all_id_admin
    return get_all_id_admin()


def get_chat_id():
    with open(f"{home}/chat_id.txt", "r") as f:
        return int(f.read())


def set_chat_id(new_chat_id: int):
    with open(f"{home}/chat_id.txt", "w") as f:
        return f.write(str(new_chat_id))


settings = get_settings()

scope_sheet = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file(f'{home}/cred.json')

client_sheet = gspread.authorize(credentials.with_scopes(scope_sheet))
sheet = client_sheet.open_by_url(config('sheet'))

calendar = GoogleCalendar(config("calendar"), credentials=credentials)

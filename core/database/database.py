import sqlite3

import datetime as dt

from core.settings import settings, home


def save_new_user(user_id: int, link: str) -> None:
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        data = [user_id, link, dt.date.strftime(dt.date.today(), '%d.%m.%Y')]
        cursor = connect.cursor()
        cursor.execute('SELECT EXISTS(SELECT * FROM all_user where user_id = $1)', [user_id])
        if bool(cursor.fetchall()[0][0]):
            return
        cursor.execute('INSERT INTO main.all_user (user_id, link, data_registr) VALUES(?, ?, ?);', data)


def get_all_id_admin() -> list[int]:
    """:return: список id администраторов"""
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute('SELECT user_id FROM main.all_user WHERE admin=true')
        list_id = cursor.fetchall()
        result = [i[0] for i in list_id]
        result.append(settings.bots.admin_id)
    return result


def get_all_id_user() -> list[int]:
    """:return: список id администраторов"""
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute('SELECT user_id FROM main.all_user')
        list_id = cursor.fetchall()
    return [i[0] for i in list_id]


def get_scope_user(user_id: int) -> int:
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute('SELECT score FROM main.all_user WHERE user_id=$1', [user_id])
    return cursor.fetchall()[0][0]


def get_all_data_admin() -> dict:
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute('SELECT user_id, name FROM main.all_user WHERE admin=true')
        list_id = cursor.fetchall()
        result = {i[0]: i[1] for i in list_id}
    return result


def get_all_data_user() -> list:
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM main.all_user')
    return cursor.fetchall()


def get_all_birthdate_user() -> list:
    today = dt.date.strftime(dt.date.today(), '%d.%m.%Y')
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute('SELECT user_id FROM main.all_user where birthday=$1', [today])
    return [i[0] for i in cursor.fetchall()]


def save_new_admin(user_id: int, link: str, name:str) -> None:
    save_new_user(user_id, link)
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute('UPDATE main.all_user SET admin=true, name=$1 WHERE user_id=$2', [name, user_id])


def get_mess(type_mess: str) -> dict:
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute(f'SELECT text, photo_id, link FROM main.message WHERE type_message=$1', [type_mess])
        data = cursor.fetchall()[0]
        result = {"text": data[0], "photo_id": data[1],  "link": data[2]}
        return result


def get_service(type_mess: str) -> dict:
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute(f'SELECT description, photo_id, amount, name FROM main.service WHERE type=$1', [type_mess])
        data = cursor.fetchall()[0]
        result = {"description": data[0], "photo_id": data[1],  "amount": data[2], "name": data[3]}
        return result


def get_user_name(user_id: int) -> str:
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute(f'SELECT name FROM main.all_user WHERE user_id=$1', [user_id])
        return cursor.fetchall()[0][0]


def set_mess(type_mess: str, text: str, photo_id: str = None, link: str = None) -> None:
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute('UPDATE main.message SET text=$1, photo_id=$2, link=$3 WHERE type_message=$4',
                       [text, photo_id, link, type_mess])


def deleted_admin(user_id: int):
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute(f'UPDATE main.all_user SET admin=false WHERE user_id=$1',
                       [user_id])


def update_message(data: dict):
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute(f'UPDATE main.message SET text=$1, photo_id=$2, link=$3 WHERE type_message=$4',
                       [data['text'], data['photo_id'], data['link'], data['type_mess']])


def update_score_user(new_score: int, user_id: int):
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute(f'UPDATE main.all_user SET score=$1 WHERE user_id=$2', [new_score, user_id])


def update_photo_id(type_mess: str, new_photo_id: str):
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute(f'UPDATE main.message SET photo_id=$1 WHERE type_message=$2', [new_photo_id, type_mess])


def check_birthday(user_id: int):
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute(f'SELECT birthday FROM main.all_user where user_id = $1', [user_id])
        data = cursor.fetchall()[0][0]
        if data is None:
            return False
        return True


def update_birthday(date: str, user_id: int):
    with sqlite3.connect(f"{home}/database/main_data.db") as connect:
        cursor = connect.cursor()
        cursor.execute(f'UPDATE main.all_user SET birthday=$1 WHERE user_id=$2', [date, user_id])

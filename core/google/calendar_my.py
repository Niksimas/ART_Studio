import datetime as dt
from gcsa.event import Event
from core.settings import calendar as cl


def set_event(data: dict):
    day = int(data["date"].split(".")[0])
    month = int(data["date"].split(".")[1])
    year = int(data["date"].split(".")[2])
    time_start = int(data['time'].split(":")[0])
    time_stop = int(data['time'].split(" - ")[-1].split(":")[0])
    event = Event(
        summary=data['name'],
        start=dt.datetime(year=year, month=month, day=day, hour=time_start),
        end=dt.datetime(year=year, month=month, day=day, hour=time_stop),
        description=f"Мероприятие: {data['name']}\n"
                    f"ФИО: {data['FIO']}\n"
                    f"Контакт: {data['phone']}\n"
                    f"Дата: {data['date']}\n"
                    f"Время: {data['time']}\n"
                    f"Тип оплаты: {data['name_amount']}\n"
    )
    cl.add_event(event)

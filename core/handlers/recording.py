import re
import datetime as dt

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, LabeledPrice, ReplyKeyboardRemove, PreCheckoutQuery

from core.keyboard import reply as kbr
from core.keyboard import inline as kbi
from core.database import database as db
from core.google.calendar_my import set_event
from core.settings import get_chat_id, settings

subrouter = Router()


class Recording(StatesGroup):
    FIO = State()
    Phone = State()
    Date = State()
    Time = State()
    CheckMessage = State()
    CheckScore = State()
    Amount = State()


@subrouter.callback_query(F.data.startswith("registration_"))
@subrouter.callback_query(F.data == "no", Recording.CheckMessage)
async def registration_in_service(call: CallbackQuery, state: FSMContext):
    try:
        msg = await call.message.edit_text("Укажите свои ФИО:", reply_markup=kbi.return_service(call.data.split("_")[-1]))
    except TelegramBadRequest:
        msg = await call.message.answer("Укажите свои ФИО:", reply_markup=kbi.return_service(call.data.split("_")[-1]))
        await call.message.delete()
    await state.set_state(Recording.FIO)
    await state.update_data({"service": call.data.split("_")[-1], "del": msg.message_id})


@subrouter.message(Recording.FIO)
async def registration_in_service(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(mess.chat.id, data['del'], reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    await mess.answer("Поделитесь номером с помощью кнопки ниже (отправиться привязанный к аккаунту номер) "
                      "или напишите иной номер", reply_markup=kbr.share_number())
    await state.set_state(Recording.Phone)
    await state.update_data(FIO=mess.text)


@subrouter.message(Recording.Phone)
async def set_city_form(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(mess.chat.id, data['del'], reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    try:
        await state.update_data({"phone": mess.contact.phone_number})
    except AttributeError:
        regex = re.compile("\+?\d[\( -]?\d{3}[\) -]?\d{3}[ -]?\d{2}[ -]?\d{2}")
        numbers = re.findall(regex, mess.text)
        phone = [] == numbers
        if phone:
            msg = await mess.answer("Я не смог распознать номер телефона. Пожалуйста нажмите кнопку "
                                    "\"Поделиться контактом\" или проверьте правильность указанного номера!",
                                    reply_markup=kbi.to_return())
            await state.update_data({"del": msg.message_id})
            return
        await state.update_data({"phone": mess.text})
    await mess.answer("Телефон сохранен!", reply_markup=ReplyKeyboardRemove())
    await mess.answer("Выберите желаемую дату:", reply_markup=kbi.kalendar(dt.date.today()))
    await state.set_state(Recording.Date)
    return


@subrouter.callback_query(Recording.Time, F.data == "back_time")
async def view_next_month(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Выберите желаемую дату:", reply_markup=kbi.kalendar(dt.date.today()))
    await state.set_state(Recording.Date)


@subrouter.callback_query(Recording.Date, F.data.split("-")[0] == "next")
async def view_next_month(call: CallbackQuery):
    in_data = dt.date(int(call.data.split("-")[1]), int(call.data.split("-")[2]), int(call.data.split("-")[3]))
    stop_day = dt.datetime.today() + dt.timedelta(days=32)
    if dt.date(stop_day.year, stop_day.month, 1) > in_data:
        await call.message.edit_reply_markup(
            reply_markup=kbi.kalendar(kbi.adding_month(in_data)))
    else:
        await call.answer("Доступных дат больше нет")


@subrouter.callback_query(Recording.Date, F.data.split("-")[0] == "back")
async def view_back_month(call: CallbackQuery):
    in_data = dt.date(int(call.data.split("-")[1]), int(call.data.split("-")[2]), int(call.data.split("-")[3]))
    stop_day = dt.datetime.today()
    if dt.date(stop_day.year, stop_day.month, 1) < in_data:
        await call.message.edit_reply_markup(
            reply_markup=kbi.kalendar(kbi.subtracting_month(in_data)))
    else:
        await call.answer("Доступных дат больше нет")


@subrouter.callback_query(Recording.Date, F.data == "month")
async def answer_month(call: CallbackQuery):
    await call.answer("Выберите дату в представленном месяце")


@subrouter.callback_query(Recording.Date, F.data.split("-")[0] == "setd")
async def save_date_start(call: CallbackQuery, state: FSMContext):
    if call.data.split("-")[1] != "":
        if int(call.data.split("-")[2]) < 10:
            month = f'0{call.data.split("-")[2]}'
        else:
            month = call.data.split("-")[2]
        if int(call.data.split("-")[1]) < 10:
            day = f'0{call.data.split("-")[1]}'
        else:
            day = call.data.split("-")[1]
        await state.update_data({"date": f'{day}.{month}.{call.data.split("-")[3]}'})
        await call.message.edit_text("Выберите желаемое время:", reply_markup=kbi.time_record(int(day)))
        await state.set_state(Recording.Time)
    else:
        await call.answer("Данная дата недоступна для записи.")


@subrouter.callback_query(Recording.Time, F.data.startswith("time_"))
async def answer_month(call: CallbackQuery, state: FSMContext):
    if call.data.find("-") < 0:
        await call.answer("Это время не доступно для записи!")
    await state.update_data(time=call.data.split("_")[-1])
    data = await state.get_data()
    data_service = db.get_service(data['service'])
    await state.update_data(data_service)
    await call.message.edit_text(f"Мероприятие: {data_service['name']}\n"
                                 f"ФИО: {data['FIO']}\n"
                                 f"Контакт: {data['phone']}\n"
                                 f"Дата: {data['date']}\n"
                                 f"Время: {data['time']}\n\n"
                                 f"Верно?", reply_markup=kbi.check_up())
    await state.set_state(Recording.CheckMessage)


@subrouter.callback_query(Recording.CheckMessage, F.data == "yes")
async def answer_month(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score_user = db.get_scope_user(call.from_user.id)
    await state.update_data({"score_user": score_user})
    if score_user == 0:
        await call.message.edit_text("Для полного бронирования необходимо внести оплату!")
        msg = await call.message.answer_invoice(
            title="Бронирование",
            description=f"Оплата участия в {data['name']}!",
            payload="buy",
            provider_token=settings.pay_token,
            currency="RUB",
            prices=[
                LabeledPrice(label="Стоимость", amount=data["amount"]),
                LabeledPrice(label="Бонусы", amount=0),
            ]
        )
        await state.update_data({"del": msg.message_id})
        await state.set_state(Recording.Amount)
    else:
        available_score = round(data['amount'] * 0.15)
        if available_score > score_user:
            available_score = score_user
        await call.message.edit_text("Для полного бронирования необходимо внести оплату!\n"
                                     f"На вашем счету {round(score_user/100)} бонусов\n"
                                     f"Можно списать {round(available_score/100)} бонусов, списываем?",
                                     reply_markup=kbi.check_up())
        await state.update_data({"available_score": round(available_score/100)*100})
        await state.set_state(Recording.CheckScore)


@subrouter.callback_query(Recording.CheckScore, F.data == "yes")
async def answer_month(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    data = await state.get_data()
    msg = await call.message.answer_invoice(
        title="Бронирование",
        description=f"Оплата участия в {data['name']}!",
        payload="buy",
        provider_token=settings.pay_token,
        currency="RUB",
        prices=[
            LabeledPrice(label="Стоимость", amount=data["amount"]),
            LabeledPrice(label="Бонусы", amount=-data["available_score"]),
        ]
    )
    await state.update_data({"del": msg.message_id, "bonuses": True})
    await state.set_state(Recording.Amount)


@subrouter.callback_query(Recording.CheckScore, F.data == "no")
async def answer_month(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    data = await state.get_data()
    msg = await call.message.answer_invoice(
        title="Бронирование",
        description=f"Оплата участия в {data['name']}!",
        payload="buy",
        provider_token=settings.pay_token,
        currency="RUB",
        prices=[
            LabeledPrice(label="Стоимость", amount=data["amount"]),
            LabeledPrice(label="Бонусы", amount=0),
        ]
    )
    await state.update_data({"del": msg.message_id, "bonuses": False})
    await state.set_state(Recording.Amount)


@subrouter.pre_checkout_query(lambda query: True)
async def start_not_active(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@subrouter.message(F.successful_payment, Recording.Amount)
async def process_successful_payment(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await bot.delete_message(mess.from_user.id, data["del"])
    set_event(data)
    await mess.answer("Оплата принята! Вы записаны!", reply_markup=kbi.to_return())
    if data['bonuses']:
        db.update_score_user(data["score_user"] - data['available_score'], mess.from_user.id)
    else:
        db.update_score_user(data["score_user"] + (data['amount'] * 0.1), mess.from_user.id)
    await state.clear()
    await bot.send_message(get_chat_id(), f"Новая запись!\n"
                                          f"Мероприятие: {data['name']}\n"
                                          f"ФИО: {data['FIO']}\n"
                                          f"Контакт: {data['phone']}\n"
                                          f"Дата: {data['date']}\n"
                                          f"Время: {data['time']}\n\n")

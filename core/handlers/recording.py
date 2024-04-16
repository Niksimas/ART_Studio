import asyncio
import datetime as dt
import os
import re

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile, LabeledPrice, ReplyKeyboardRemove, PreCheckoutQuery

from core.database import database as db
from core.google.calendar_my import set_event
from core.keyboard import inline as kbi
from core.keyboard import reply as kbr
from core.settings import get_chat_id, settings, home

subrouter = Router()


class Recording(StatesGroup):
    TypeRecord = State()
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
    await state.set_state(Recording.Amount)
    if call.data != "no":
        await call.message.edit_reply_markup(reply_markup=kbi.choice_amount(db.get_list_amount()))
        await state.update_data({"service": call.data.split("_")[-1]})
    else:
        data = db.get_service((await state.get_data())["service"])
        message = f"{data['name']}\n{data['description']}"
        if data["photo_id"] is not None:
            try:
                await call.message.answer_photo(data["photo_id"], caption=message,
                                                reply_markup=kbi.choice_amount(db.get_list_amount()))
                await call.message.delete()
            except TelegramBadRequest:
                destination = f'{home}/photo/{data["photo_id"]}.jpg'
                msg = await call.message.answer_photo(photo=FSInputFile(destination), caption=message,
                                                 reply_markup=kbi.choice_amount(db.get_list_amount()))
                if os.path.exists(destination):
                    os.rename(destination, f"{home}/photo/{msg.photo[-1].file_id}.jpg")
                db.update_photo_id("start", msg.photo[-1].file_id)
        else:
            try:
                await call.message.edit_text(message, reply_markup=kbi.choice_amount(db.get_list_amount()))
            except TelegramBadRequest:
                await call.message.answer(message, reply_markup=kbi.choice_amount(db.get_list_amount()))
                await call.message.delete()
""

@subrouter.callback_query(F.data.startswith("amount_"), Recording.Amount)
async def registration_in_service(call: CallbackQuery, state: FSMContext):
    try:
        msg = await call.message.edit_text("Укажите свои ФИО:", reply_markup=kbi.return_service(call.data.split("_")[-1]))
    except TelegramBadRequest:
        msg = await call.message.answer("Укажите свои ФИО:", reply_markup=kbi.return_service(call.data.split("_")[-1]))
        await call.message.delete()
    await state.set_state(Recording.FIO)
    await state.update_data({"del": msg.message_id, "id_amount": int(call.data.split("_")[-1])})


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


@subrouter.message(F.text == "Отмена", Recording.Phone)
async def registration_in_service(mess: Message, state: FSMContext):
    data = await state.get_data()
    data_mess = db.get_service(data["service"])
    message = f"{data_mess['name']}\n{data_mess['description']}"
    await mess.answer("Ожидание снято!", reply_markup=ReplyKeyboardRemove())
    try:
        await mess.answer_photo(data_mess["photo_id"], caption=message,
                                reply_markup=kbi.menu_service_send(data["service"], mess.from_user.id))
    except TelegramBadRequest:
        destination = f'{home}/photo/{data_mess["photo_id"]}.jpg'
        msg = await mess.answer_photo(photo=FSInputFile(destination), caption=message,
                                      reply_markup=kbi.menu_service_send(data["service"], mess.from_user.id))
        if os.path.exists(destination):
            os.rename(destination, f"{home}/photo/{msg.photo[-1].file_id}.jpg")
        db.update_photo_id("start", msg.photo[-1].file_id)


@subrouter.message(Recording.Phone)
async def set_city_form(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(mess.chat.id, data['del'], reply_markup=None)
    except (KeyError, TelegramBadRequest):
        pass
    if data['service'] == "1":
        all_day = True
    else:
        all_day = False
    try:
        await state.update_data({"phone": mess.contact.phone_number, "all_day": all_day})
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
        await state.update_data({"phone": mess.text, "all_day": all_day})
    await mess.answer("Телефон сохранен!", reply_markup=ReplyKeyboardRemove())

    await mess.answer("Выберите желаемую дату:", reply_markup=kbi.kalendar(dt.date.today(), all_day,
                                                                           cancel_cd="service_" + data['service']))
    await state.set_state(Recording.Date)
    return


@subrouter.callback_query(Recording.Time, F.data == "back_time")
async def view_next_month(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_text("Выберите желаемую дату:", reply_markup=kbi.kalendar(dt.date.today(), data['all_day'],
                                                                                   cancel_cd="service_" + data['service']))
    await state.set_state(Recording.Date)


@subrouter.callback_query(Recording.Date, F.data.split("-")[0] == "next")
async def view_next_month(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    in_data = dt.date(int(call.data.split("-")[1]), int(call.data.split("-")[2]), int(call.data.split("-")[3]))
    stop_day = dt.datetime.today() + dt.timedelta(days=32)
    if dt.date(stop_day.year, stop_day.month, 1) > in_data:
        await call.message.edit_reply_markup(
            reply_markup=kbi.kalendar(kbi.adding_month(in_data), data['all_day'], cancel_cd="service_" + data['service']))
    else:
        await call.answer("Доступных дат больше нет")


@subrouter.callback_query(Recording.Date, F.data.split("-")[0] == "back")
async def view_back_month(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    in_data = dt.date(int(call.data.split("-")[1]), int(call.data.split("-")[2]), int(call.data.split("-")[3]))
    stop_day = dt.datetime.today()
    if dt.date(stop_day.year, stop_day.month, 1) < in_data:
        await call.message.edit_reply_markup(
            reply_markup=kbi.kalendar(kbi.subtracting_month(in_data), data['all_day'], cancel_cd="service_" + data['service']))
    else:
        await call.answer("Доступных дат больше нет")


@subrouter.callback_query(Recording.Date, F.data == "month")
async def answer_month(call: CallbackQuery):
    await call.answer("Выберите дату в представленном месяце")


@subrouter.callback_query(Recording.Date, F.data.split("-")[0] == "setd")
async def save_date_start(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data.split("-")[1] != "":
        if int(call.data.split("-")[2]) < 10:
            month = f'0{call.data.split("-")[2]}'
        else:
            month = call.data.split("-")[2]
        if int(call.data.split("-")[1]) < 10:
            day = f'0{call.data.split("-")[1]}'
        else:
            day = call.data.split("-")[1]
        week_day = dt.date(int(call.data.split("-")[3]), int(call.data.split("-")[2]), int(call.data.split("-")[1])).weekday()
        await state.update_data({"date": f'{day}.{month}.{call.data.split("-")[3]}'})
        await call.message.edit_text("Выберите желаемое время:", reply_markup=kbi.time_record(int(day), week_day,
                                                                                              cancel_cd="service_" + data['service']))
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
    data_amount = db.get_amount_service(data['id_amount'])
    await state.update_data(data_service)
    await call.message.edit_text(f"Мероприятие: {data_service['name']}\n"
                                 f"ФИО: {data['FIO']}\n"
                                 f"Контакт: {data['phone']}\n"
                                 f"Дата: {data['date']}\n"
                                 f"Время: {data['time']}\n"
                                 f"Тип услуги: {data_amount['name_amount']}:\n"
                                 f"Стоимость: {data_amount['amount']}р.\n"
                                 f"Верно?", reply_markup=kbi.check_up("service_" + data['service']))
    await state.set_state(Recording.CheckMessage)


@subrouter.callback_query(Recording.CheckMessage, F.data == "yes")
async def answer_month(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    score_user = db.get_scope_user(call.from_user.id)
    await state.update_data({"score_user": score_user})
    data_amount = db.get_amount_service(data['id_amount'])
    if score_user == 0:
        await call.message.edit_text("Для полного бронирования необходимо внести оплату!")
        msg = await call.message.answer_invoice(
            title="Бронирование",
            description=f"Оплата участия в {data['name']}!",
            payload="buy",
            provider_token=settings.pay_token,
            currency="RUB",
            prices=[
                LabeledPrice(label=data_amount['name_amount'], amount=data_amount["amount"]*100),
                LabeledPrice(label="Бонусы", amount=0),
            ],
            reply_markup=kbi.return_invoice(data['service'])
        )
        await state.update_data({"del": msg.message_id})
        await state.set_state(Recording.Amount)
        try:
            await asyncio.sleep(900)
            await bot.delete_message(call.from_user.id, msg.message_id)
            await state.clear()
        except TelegramBadRequest:
            pass
    else:
        available_score = round(data_amount['amount'] * 0.15)
        if available_score > score_user:
            available_score = score_user
        await call.message.edit_text("Для полного бронирования необходимо внести оплату!\n"
                                     f"На вашем счету {round(score_user/100)} бонусов\n"
                                     f"Можно списать {round(available_score/100)} бонусов, списываем?",
                                     reply_markup=kbi.check_up())
        await state.update_data({"available_score": round(available_score/100)*100})
        await state.set_state(Recording.CheckScore)


@subrouter.callback_query(Recording.CheckScore, F.data == "yes")
async def answer_month(call: CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.delete()
    data = await state.get_data()
    data_amount = db.get_amount_service(data['id_amount'])
    msg = await call.message.answer_invoice(
        title="Бронирование",
        description=f"Оплата участия в {data['name']}!",
        payload="buy",
        provider_token=settings.pay_token,
        currency="RUB",
        prices=[
            LabeledPrice(label=data_amount['name_amount'], amount=data_amount["amount"]*100),
            LabeledPrice(label="Бонусы", amount=-data["available_score"]),
        ],
        reply_markup=kbi.return_invoice(data['service'])
    )
    await state.update_data({"del": msg.message_id, "bonuses": True})
    await state.set_state(Recording.Amount)
    try:
        await asyncio.sleep(900)
        await bot.delete_message(call.from_user.id, msg.message_id)
        await state.clear()
    except TelegramBadRequest:
        pass


@subrouter.callback_query(Recording.CheckScore, F.data == "no")
async def answer_month(call: CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.delete()
    data = await state.get_data()
    data_amount = db.get_amount_service(data['id_amount'])
    msg = await call.message.answer_invoice(
        title="Бронирование",
        description=f"Оплата участия в {data['name']}!",
        payload="buy",
        provider_token=settings.pay_token,
        currency="RUB",
        prices=[
            LabeledPrice(label=data_amount['name_amount'], amount=data_amount["amount"]*100),
            LabeledPrice(label="Бонусы", amount=0),
        ],
        reply_markup=kbi.return_invoice(data['service'])
    )
    await state.update_data({"del": msg.message_id, "bonuses": False})
    await state.set_state(Recording.Amount)
    try:
        await asyncio.sleep(900)
        await bot.delete_message(call.from_user.id, msg.message_id)
        await state.clear()
    except TelegramBadRequest:
        pass


@subrouter.pre_checkout_query(lambda query: True)
async def start_not_active(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@subrouter.message(F.successful_payment, Recording.Amount)
async def process_successful_payment(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await bot.delete_message(mess.from_user.id, data["del"])
    data_amount = db.get_amount_service(data['id_amount'])
    data = dict(list(data_amount.items()) + list(data.items()))
    set_event(data)
    await mess.answer("Оплата принята! Вы записаны!", reply_markup=kbi.to_return())
    if data['bonuses']:
        db.update_score_user(data["score_user"] - data['available_score'], mess.from_user.id)
    else:
        db.update_score_user(data["score_user"] + (data_amount['amount'] * 0.1), mess.from_user.id)
    await state.clear()
    await bot.send_message(get_chat_id(), f"Новая запись!\n"
                                          f"Мероприятие: {data['name']}\n"
                                          f"ФИО: {data['FIO']}\n"
                                          f"Контакт: {data['phone']}\n"
                                          f"Дата: {data['date']}\n"
                                          f"Время: {data['time']}\n"
                                          f"Тип оплаты: {data_amount['name_amount']}\n")

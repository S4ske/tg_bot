from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from src.api import API
from src.dto.schemas import Waybill
from src.dto.states import Menu
from src.utils import validate_response
from telegram.beauty_print import print_waybill
from telegram.keyboards import main_keyboard_markup, waybill_markup

router = Router()


@router.message(Menu.checking_waybills, F.text.casefold() == "назад")
@router.message(Menu.waybill, F.text.casefold() == "назад")
@router.message(Menu.starting_work, F.text.casefold() == "назад")
@router.message(Menu.stopping_work, F.text.casefold() == "назад")
async def back(message: Message, state: FSMContext):
    await state.set_state(Menu.main)
    await message.answer("Возвращение...", reply_markup=main_keyboard_markup)


@router.message(Menu.checking_waybills)
async def select_waybill(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    token = data["token"]
    calendar_tasks_resp = await API.get_calendar_tasks(token)
    try:
        calendar_task = list(
            filter(lambda x: x.id == int(message.text), calendar_tasks_resp.get)
        )[0]
    except IndexError:
        await message.answer("Введите номер существующего задания")
        return
    if not calendar_task.idWaybill:
        await message.answer("У этого задания нет путевого листа")
        return
    waybill_resp = await API.get_waybill(token, calendar_task.idWaybill)
    if waybill_resp and waybill_resp.success:
        waybill = waybill_resp.get
        await state.set_state(Menu.waybill)
        await state.update_data(waybill=waybill.model_dump())
        await message.answer(
            f"Вы выбрали задание №{message.text}", reply_markup=waybill_markup
        )
    else:
        await message.answer("Что-то пошло не так")


@router.message(Menu.waybill, F.text.casefold() == "информация")
async def waybill_information(message: Message, state: FSMContext):
    data = await state.get_data()
    waybill = Waybill(**data["waybill"])
    await message.answer(print_waybill(waybill))


@router.message(Menu.waybill, F.text.casefold() == "начать/завершить работу")
async def start_stop_work(message: Message, state: FSMContext):
    data = await state.get_data()
    waybill = Waybill(**data["waybill"])
    if waybill.dateEnd:
        await message.answer("Работы завершены")
    elif waybill.dateStart:
        await message.answer(
            "Введите значение одометра в конце",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Назад")]]),
        )
        await state.set_state(Menu.stopping_work)
    else:
        await message.answer(
            "Введите значение одометра на старте",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Назад")]]),
        )
        await state.set_state(Menu.starting_work)


@router.message(Menu.starting_work)
async def start_work(message: Message, state: FSMContext):
    data = await state.get_data()
    token = data["token"]
    waybill = Waybill(**data["waybill"])
    start_resp = await API.start_waybill(token, waybill.id, int(message.text))
    if not await validate_response(message, start_resp):
        return
    await message.answer("Работа начата", reply_markup=waybill_markup)
    await state.set_state(Menu.waybill)


@router.message(Menu.stopping_work)
async def stop_work(message: Message, state: FSMContext):
    data = await state.get_data()
    token = data["token"]
    waybill = Waybill(**data["waybill"])
    stop_resp = await API.stop_waybill(token, waybill.id, int(message.text))
    if not await validate_response(message, stop_resp):
        return
    await message.answer("Работа закончена", reply_markup=waybill_markup)
    await state.set_state(Menu.waybill)

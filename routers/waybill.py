from aiogram import Router, F

import schemas
from schemas import Menu
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from api import API
import beauty_print

router = Router()


@router.message(Menu.main, F.text.casefold() == 'выбрать путевой лист')
async def check_calendar_tasks(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    resp = await API.get_calendar_tasks(data['token'])
    if resp.success:
        calendar_tasks = resp.get
        await state.set_state(Menu.checking_waybill)
        await message.answer('Введите номер путевого листа',
                             reply_markup=ReplyKeyboardMarkup(
                                 keyboard=[[KeyboardButton(text=str(task.idWaybill))] for task in calendar_tasks
                                           if task.idWaybill]
                                          + [[KeyboardButton(text='Назад')]]))
    else:
        await message.answer('Что-то пошло не так')


@router.message(Menu.checking_waybill)
async def check_calendar_task(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    try:
        resp = await API.get_waybill(data['token'], int(message.text))
    except:
        await message.answer('Введите номер путевого листа')
        return
    await state.set_state(Menu.main)
    if resp.success:
        waybill = resp.get
        await message.answer(beauty_print.print_Waybill(waybill), reply_markup=schemas.main_keyboard_markup)
    else:
        await state.set_state(Menu.main)
        await message.answer('Что-то пошло не так')

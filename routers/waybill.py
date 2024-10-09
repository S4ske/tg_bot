from aiogram import Router, F
from schemas import Menu, Waybill
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from api import API
from utils import waybill_markup, main_keyboard_markup

router = Router()


@router.message(Menu.checking_waybill)
async def select_waybill(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    token = data['token']
    calendar_tasks_resp = await API.get_calendar_tasks(token)
    try:
        calendar_task = list(filter(lambda x: x.id == int(message.text), calendar_tasks_resp.get))[0]
    except IndexError:
        await message.answer('Введите номер существующего задания')
        return
    if not calendar_task.idWaybill:
        await message.answer('У этого задания нет путевого листа')
        return
    waybill_resp = await API.get_waybill(token, calendar_task.idWaybill)
    if waybill_resp.success:
        waybill = waybill_resp.get
        await state.set_state(Menu.waybill)
        await state.update_data(waybill=waybill.model_dump())
        await message.answer(f'Вы выбрали задание {message.text}', reply_markup=waybill_markup)
    else:
        await message.answer('Что-то пошло не так')


@router.message(Menu.waybill, F.text.casefold() == 'информация')
async def waybill_information(message: Message, state: FSMContext):
    data = await state.get_data()
    waybill = Waybill(**data['waybill'])
    await message.answer(str(waybill.model_dump()))


@router.message(Menu.checking_waybill, F.text.casefold() == 'назад')
@router.message(Menu.waybill, F.text.casefold() == 'назад')
async def back(message: Message, state: FSMContext):
    await state.set_state(Menu.main)
    await message.answer('Возвращение...', reply_markup=main_keyboard_markup)

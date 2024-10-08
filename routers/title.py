from aiogram import Router, F
from aiogram.types import Message
from api import API
from states import Menu
from aiogram.fsm.context import FSMContext
from utils import get_keyboard_markup_calendar_tasks
from beauty_print import print_calendar_task

router = Router()


@router.message(Menu.main, F.text.casefold() == 'мои задания')
async def get_calendar_tasks(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    response = await API.get_calendar_tasks(data['token'])
    if response and response.success:
        calendar_tasks = response.get
        if not calendar_tasks:
            await message.answer('<b>У вас нет заданий</b>')
        else:
            await state.set_state(Menu.checking_waybills)
            await message.answer('<b>Ваши задания:</b>', reply_markup=get_keyboard_markup_calendar_tasks(calendar_tasks))
            for task in calendar_tasks:
                await message.answer(print_calendar_task(task))
    else:
        await message.answer('Что-то пошло не так')


@router.message(Menu.main, F.text.casefold() == 'мои задания на сегодня')
async def get_current_calendar_tasks(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    response = await API.get_current_calendar_tasks(data['token'])
    if response and response.success:
        calendar_tasks = response.get
        if not calendar_tasks:
            await message.answer('<b>У вас нет заданий на сегодня</b>')
        else:
            await state.set_state(Menu.checking_waybills)
            await message.answer('<b>Ваши задания на сегодня:</b>',
                                 reply_markup=get_keyboard_markup_calendar_tasks(calendar_tasks))
            for task in calendar_tasks:
                await message.answer(print_calendar_task(task))
    else:
        await message.answer('Что-то пошло не так')

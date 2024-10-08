from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from api import API
from schemas import Menu
from aiogram.fsm.context import FSMContext
import beauty_print
import schemas

router = Router()


@router.message(Menu.main, F.text.casefold() == 'мои данные')
async def get_me(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    response = await API.get_me(data['token'])
    if response.success:
        await message.answer(str(response.get.model_dump()))
    else:
        await message.answer('Что-то пошло не так')


@router.message(Menu.main, F.text.casefold() == 'мои задания')
async def get_calendar_tasks(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    response = await API.get_calendar_tasks(data['token'])
    if response.success:
        calendar_tasks = response.get
        await message.answer('<b>Ваши задания</b>')
        for task in calendar_tasks:
            await message.answer(beauty_print.print_CalendarTask(task), reply_markup=ReplyKeyboardMarkup(
                                 keyboard=[[KeyboardButton(text=str(task.id))] for task in calendar_tasks
                                           if task.id]
                                          + [[KeyboardButton(text='Назад')]])) # добавила вывод кнопок с номерами заданий
    else:
        await message.answer('Что-то пошло не так')



# недоделанный неработающий метод для вывода описания задания


@router.message(Menu.checking_task)
async def check_calendar_task(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    try:
        resp = await API.get_task(data['token'], int(message.text))
    except:
        await message.answer('Введите номер задания')
        return
    await state.set_state(Menu.main)
    if resp.success:
        task = resp.get
        await message.answer(beauty_print.print_Task(task), reply_markup=schemas.main_keyboard_markup)
    else:
        await state.set_state(Menu.main)
        await message.answer('Что-то пошло не так')









@router.message(Menu.main, F.text.casefold() == 'мои задания на сегодня')
async def get_current_calendar_tasks(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    response = await API.get_current_calendar_tasks(data['token'])
    if response.success:
        text = "<b>Ваши задания на сегодня</b>"
        await message.answer(f"{text:^15}")
        current_calendar_tasks = response.get
        for task in current_calendar_tasks:
            await message.answer(beauty_print.print_CalendarTask(task))
    else:
        await message.answer('Что-то пошло не так')

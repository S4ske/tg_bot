from aiogram import Router, F
from aiogram.types import Message
from api import API
from schemas import Menu
from aiogram.fsm.context import FSMContext

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
        await message.answer(str(list(map(lambda x: x.model_dump(), response.get))))
    else:
        await message.answer('Что-то пошло не так')


@router.message(Menu.main, F.text.casefold() == 'мои задания на сегодня')
async def get_current_calendar_tasks(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    response = await API.get_current_calendar_tasks(data['token'])
    if response.success:
        await message.answer(str(list(map(lambda x: x.model_dump(), response.get))))
    else:
        await message.answer('Что-то пошло не так')

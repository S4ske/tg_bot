from aiogram import Router, F
from aiogram.types import ReplyKeyboardRemove, Message
from aiogram.fsm.context import FSMContext
from schemas import Credentials, Menu
from api import API
from utils import main_keyboard_markup

router = Router()


@router.message(Credentials.login)
async def login(message: Message, state: FSMContext) -> None:
    await state.update_data(login=message.text)
    await state.set_state(Credentials.password)
    await message.answer('Отлично, теперь отправь свой пароль', reply_markup=ReplyKeyboardRemove())


@router.message(Credentials.password)
async def password(message: Message, state: FSMContext) -> None:
    await state.update_data(password=message.text)
    data = await state.get_data()
    login_response = await API.login(data['login'], data['password'])
    if login_response and login_response.success:
        await state.set_state(Menu.main)
        await state.update_data(token=login_response.token)
        await message.answer('Вы успешно авторизировались', reply_markup=main_keyboard_markup)
    else:
        await state.clear()
        await message.answer('Неправильный логин или пароль')


@router.message(F.text.casefold() == 'выйти из аккаунта')
async def logout(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Вы успешно вышли', reply_markup=ReplyKeyboardRemove())

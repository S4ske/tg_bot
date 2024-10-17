import asyncio
from redis.asyncio import Redis
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove, BotCommand
from aiogram.fsm.context import FSMContext
from states import Credentials, Menu
from aiogram.fsm.storage.redis import RedisStorage
from routers import auth, title, waybill, checklist, tasks
from utils import main_keyboard_markup

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
main_dispatcher = Dispatcher(storage=RedisStorage(Redis(host='redis')))


@main_dispatcher.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.set_state(Credentials.login)
    await message.answer('Привет! Отправь мне свой логин', reply_markup=ReplyKeyboardRemove())


@main_dispatcher.message(Command('main_menu'))
async def start(message: Message, state: FSMContext) -> None:
    curr_state = await state.get_state()
    if curr_state in ['Credentials:login', 'Credentials:password']:
        await message.answer('Вы не авторизованы')
        return
    await state.set_state(Menu.main)
    await message.answer('Возвращение...', reply_markup=main_keyboard_markup)


async def main():
    await bot.set_my_commands([BotCommand(command='/start', description='Начать работу с ботом'),
                               BotCommand(command='/main_menu', description='Вернуться в главное меню')])
    main_dispatcher.include_routers(auth.router, title.router, waybill.router, checklist.router, tasks.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await main_dispatcher.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

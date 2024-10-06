import asyncio
from redis.asyncio import Redis
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN, REDIS_HOST
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove, BotCommand
from aiogram.fsm.context import FSMContext
from schemas import Credentials
from aiogram.fsm.storage.redis import RedisStorage
from routers import auth, title, waybill

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
main_dispatcher = Dispatcher(storage=RedisStorage(redis=Redis(host=REDIS_HOST)))


@main_dispatcher.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.set_state(Credentials.login)
    await message.answer('Привет! Отправь мне свой логин', reply_markup=ReplyKeyboardRemove())


async def main():
    await bot.set_my_commands([BotCommand(command='/start', description='Начать работу с ботом')])
    main_dispatcher.include_router(auth.router)
    main_dispatcher.include_router(title.router)
    main_dispatcher.include_router(waybill.router)
    await main_dispatcher.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

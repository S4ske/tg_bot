import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from schemas import Credentials
from routers import auth, title, waybill

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


main_dispatcher = Dispatcher()


@main_dispatcher.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.set_state(Credentials.login)
    await message.answer('Привет! Отправь мне свой логин', reply_markup=ReplyKeyboardRemove())


def main():
    main_dispatcher.include_router(auth.router)
    main_dispatcher.include_router(title.router)
    main_dispatcher.include_router(waybill.router)
    asyncio.run(main_dispatcher.start_polling(bot))


if __name__ == '__main__':
    main()

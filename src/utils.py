from aiogram.types import Message

from src.api import API
from src.dto.schemas import DefaultResponse, Task


async def validate_response(
    message: Message,
    response: DefaultResponse | None,
    exception_message: str | None = None,
) -> bool:
    if not (response and response.success):
        await message.answer(
            exception_message if exception_message else "Что-то пошло не так"
        )
        return False
    return True


async def get_task_by_id(
    message: Message, token: str, waybill_id: int, task_id: int
) -> Task | None:
    task_resp = await API.get_tasks(token, waybill_id)
    if not await validate_response(message, task_resp):
        return None
    try:
        task = list(filter(lambda x: x.id == task_id, task_resp.task))[0]
    except IndexError:
        return None
    return task

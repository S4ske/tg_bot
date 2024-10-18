from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from src.api import API
from src.dto.schemas import IntermediateTaskResultIn, Task, Waybill
from src.dto.states import Menu
from src.utils import get_task_by_id, validate_response
from telegram.beauty_print import print_intermediate_task_result, print_task
from telegram.keyboards import (
    get_keyboard_markup_results,
    get_keyboard_markup_tasks,
    task_markup,
    waybill_markup,
)

router = Router()


@router.message(Menu.checking_tasks, F.text.casefold() == "назад")
@router.message(Menu.task, F.text.casefold() == "назад")
async def back(message: Message, state: FSMContext):
    await message.answer("Возвращение...", reply_markup=waybill_markup)
    await state.set_state(Menu.waybill)


@router.message(Menu.deleting_result, F.text.casefold() == "назад")
@router.message(Menu.entering_time, F.text.casefold() == "назад")
@router.message(Menu.entering_distance, F.text.casefold() == "назад")
@router.message(Menu.entering_transported, F.text.casefold() == "назад")
async def back_to_task(message: Message, state: FSMContext):
    await message.answer("Возвращение...", reply_markup=task_markup)
    await state.set_state(Menu.task)


@router.message(Menu.waybill, F.text.casefold() == "задачи")
async def get_tasks(message: Message, state: FSMContext):
    data = await state.get_data()
    token = data["token"]
    waybill = Waybill(**data["waybill"])
    task_resp = await API.get_tasks(token, waybill.id)
    if not await validate_response(message, task_resp):
        return
    tasks = task_resp.task
    if not tasks:
        await message.answer("<b>У вас нет задач</b>")
        return
    await message.answer(
        "<b>Ваши задачи в рамках путевого листа:</b>",
        reply_markup=get_keyboard_markup_tasks(tasks),
    )
    for task in tasks:
        await message.answer(print_task(task))
    await state.set_state(Menu.checking_tasks)


@router.message(Menu.checking_tasks)
async def check_task(message: Message, state: FSMContext):
    data = await state.get_data()
    token = data["token"]
    waybill = Waybill(**data["waybill"])
    task_resp = await API.get_tasks(token, waybill.id)
    if not await validate_response(message, task_resp):
        return
    tasks = task_resp.task
    try:
        task = list(filter(lambda x: x.id == int(message.text), tasks))[0]
    except IndexError:
        await message.answer("Введите номер существующей задачи")
        return
    await message.answer(f"Вы выбрали задачу №{task.id}", reply_markup=task_markup)
    await state.update_data(task=task.model_dump())
    await state.set_state(Menu.task)


@router.message(Menu.task, F.text.casefold() == "информация")
async def task_information(message: Message, state: FSMContext):
    data = await state.get_data()
    task = Task(**data["task"])
    await message.answer(print_task(task))


@router.message(Menu.task, F.text.casefold() == "список результатов")
async def results_list(message: Message, state: FSMContext):
    data = await state.get_data()
    token = data["token"]
    waybill = Waybill(**data["waybill"])
    task = Task(**data["task"])
    current_task = await get_task_by_id(message, token, waybill.id, task.id)
    if not current_task:
        return
    results = current_task.taskResult
    if not results:
        await message.answer("<b>Список результатов пуст</b>")
        return
    await message.answer("<b>Список результатов:</b>")
    for result in results:
        await message.answer(print_intermediate_task_result(result))


@router.message(Menu.task, F.text.casefold() == "завершить/продолжить задачу")
async def stop_continue_task(message: Message, state: FSMContext):
    data = await state.get_data()
    token = data["token"]
    waybill = Waybill(**data["waybill"])
    task = Task(**data["task"])
    current_task = await get_task_by_id(message, token, waybill.id, task.id)
    stop_resp = await API.stop_continue_task(
        token, waybill.id, current_task.id, not current_task.isFinished
    )
    if not await validate_response(message, stop_resp):
        return
    if current_task.isFinished:
        await message.answer("Задача продолжается")
    else:
        await message.answer("Задача завершена")


@router.message(Menu.task, F.text.casefold() == "удалить результат")
async def start_deleting_result(message: Message, state: FSMContext):
    data = await state.get_data()
    token = data["token"]
    waybill = Waybill(**data["waybill"])
    task = Task(**data["task"])
    current_task = await get_task_by_id(message, token, waybill.id, task.id)
    if not current_task:
        return
    await message.answer(
        "Введите номер результата, который хотите удалить",
        reply_markup=get_keyboard_markup_results(current_task.taskResult),
    )
    await state.set_state(Menu.deleting_result)


@router.message(Menu.deleting_result)
async def delete_result(message: Message, state: FSMContext):
    data = await state.get_data()
    token = data["token"]
    waybill = Waybill(**data["waybill"])
    delete_resp = await API.remove_task_result(token, waybill.id, int(message.text))
    if not await validate_response(message, delete_resp):
        return
    await message.answer("Результат успешно удален", reply_markup=task_markup)
    await state.set_state(Menu.task)


@router.message(Menu.task, F.text.casefold() == "добавить/редактировать результат")
async def start_adding_task(message: Message, state: FSMContext):
    await message.answer(
        "Введите время прибытия <b>строго</b> в следующем формате: ЧЧ:ММ",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Назад")]]),
    )
    await state.set_state(Menu.entering_time)


@router.message(Menu.entering_time)
async def enter_time(message: Message, state: FSMContext):
    await message.answer("Введите расстояние, которое проехали")
    await state.update_data(time=message.text)
    await state.set_state(Menu.entering_distance)


@router.message(Menu.entering_distance)
async def enter_distance(message: Message, state: FSMContext):
    await message.answer("Введите сколько тонн груза вы перевезли")
    await state.update_data(distance=message.text)
    await state.set_state(Menu.entering_transported)


@router.message(Menu.entering_transported)
async def enter_transported(message: Message, state: FSMContext):
    data = await state.get_data()
    token = data["token"]
    waybill = Waybill(**data["waybill"])
    task = Task(**data["task"])
    time = data["time"]
    distance = data["distance"]
    request = IntermediateTaskResultIn(
        arrivalTime=time, distance=distance, idTask=task.id, transported=message.text
    )
    add_resp = await API.add_task_result(token, waybill.id, request)
    if not await validate_response(message, add_resp):
        return
    await message.answer("Результат успешно добавлен", reply_markup=task_markup)
    await state.set_state(Menu.task)

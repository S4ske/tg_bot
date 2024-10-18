from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from src.dto.schemas import (
    Button,
    CalendarTask,
    Checklist,
    IntermediateTaskResult,
    Task,
)

main_keyboard_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Мои задания"),
            KeyboardButton(text="Мои задания на сегодня"),
        ],
        [KeyboardButton(text="Выйти из аккаунта")],
    ]
)

waybill_markup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Информация")],
        [KeyboardButton(text="Начать/Завершить работу")],
        [KeyboardButton(text="Контрольные листы")],
        [KeyboardButton(text="Задачи")],
        [KeyboardButton(text="Назад")],
    ]
)

default_checklist_markup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Назад")],
        [KeyboardButton(text="Покинуть контрольный лист")],
    ]
)

checkbox_markup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да"), KeyboardButton(text="Нет")],
        [KeyboardButton(text="Назад")],
        [KeyboardButton(text="Покинуть контрольный" " лист")],
    ]
)

task_markup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Информация")],
        [KeyboardButton(text="Завершить/Продолжить задачу")],
        [KeyboardButton(text="Список результатов")],
        [
            KeyboardButton(text="Добавить/Редактировать результат"),
            KeyboardButton(text="Удалить результат"),
        ],
        [KeyboardButton(text="Назад")],
    ]
)


def get_keyboard_markup_calendar_tasks(
    tasks: list[CalendarTask],
) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=str(task.id))] for task in tasks if task.idWaybill
        ]
        + [[KeyboardButton(text="Назад")]]
    )


def get_keyboard_markup_checklists(checklists: list[Checklist]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=str(checklist.id))] for checklist in checklists]
        + [[KeyboardButton(text="Назад")]]
    )


def get_keyboard_markup_buttons(buttons: list[Button]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=str(button.name))] for button in buttons]
        + [
            [KeyboardButton(text="Назад")],
            [KeyboardButton(text="Покинуть контрольный лист")],
        ]
    )


def get_keyboard_markup_tasks(tasks: list[Task]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=str(task.id))] for task in tasks]
        + [[KeyboardButton(text="Назад")]]
    )


def get_keyboard_markup_results(
    results: list[IntermediateTaskResult],
) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=str(result.id))] for result in results]
        + [[KeyboardButton(text="Назад")]]
    )

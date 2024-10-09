from schemas import CalendarTask
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Мои задания'),
                                                      KeyboardButton(text='Мои задания на сегодня')],
                                                     [KeyboardButton(text='Выйти из аккаунта')]])

waybill_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Информация')],
                                               [KeyboardButton(text='Начать/Завершить работу')],
                                               [KeyboardButton(text='Контрольные листы')],
                                               [KeyboardButton(text='Задачи')],
                                               [KeyboardButton(text='Назад')]])


def get_keyboard_markup_calendar_tasks(tasks: list[CalendarTask]):
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=str(task.id))] for task in tasks
                                         if task.idWaybill] + [[KeyboardButton(text='Назад')]])

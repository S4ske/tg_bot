from schemas import CalendarTask, Waybill, Task, IntermediateTaskResult,Checklist


def print_calendar_task(calendar_task: CalendarTask) -> str:
    return (f'Задание <b>№{calendar_task.id}</b>\n'
            f"Дата: <u>{calendar_task.calendarDate[:10]}</u>\n"
            f'Продолжительность: {calendar_task.calendarDuration}ч\n'
            f'Время начала работы: <u>{calendar_task.calendarTime[:5]}</u>\n'
            f'Наименование техники: {calendar_task.machine}'
            + ('' if calendar_task.idWaybill else '\n<b>Нет путевого листа</b>'))


def print_waybill(waybill: Waybill) -> str:
    return (f'Путевой лист <b>№{waybill.id}</b>\n'
            f'Дата: <u>{waybill.date[:10]}</u>\n'
            f'Продолжительность: {waybill.duration}ч\n'
            f'Гос.номер: {waybill.govNumber}\n'
            f'Значение одометра в конце: {waybill.mileageEnd}\n'
            f'Значение одометра на старте: {waybill.mileageStart}\n'
            f'Тип техники: {waybill.typeM}')


def print_task(task: Task) -> str:
    return (f'Задание <b>№{task.id}</b>\n'
            f'Заказчик: {task.order}\n'
            f'Время прибытия: <u>{task.arrivalTime}</u>\n'
            f'Адрес погрузки: {task.loadingAddress}\n'
            f'Адресс разгрузки: {task.unloadingAddress}\n'
            f'Наименование груза: {task.cargoName}\n'
            f'Количество ездок: {task.count}\n'
            f'Расстояние: {task.distance} км\n'
            f'Перевезти: {task.transported} тонн\n'
            f'Примечание {task.description}')

def print_intermediate_task_result(result: IntermediateTaskResult):
        return (f'Результат <b>№{result.id}</b>\n'
            f'Количество ездок: {result.count}\n'
            f'Время прибытия: <u>{result.arrivalTime}</u>\n'
            f'Расстояние: {result.distance} км\n'
            f'Перевезено: {result.transported} т')

def print_checklist(checklist: Checklist):
        return (f'Контрольный лист <b>№{checklist.checklistWaybillId}</b>\n'
                f'Название теста: {checklist.name}\n'
                f'Дата завершения теста: <u>{checklist.dateFinish}</u>\n')


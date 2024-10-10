def print_calendar_task(calendar_task):
    return (f'Задание <b>№{calendar_task.id}</b>\n'
            f"Дата: <u>{calendar_task.calendarDate[:10]}</u>\n"
            f'Продолжительность: {calendar_task.calendarDuration}ч\n'
            f'Время начала работы: <u>{calendar_task.calendarDate[:10]}</u>\n'
            f'Наименование техники: {calendar_task.machine}\n')


def print_waybill(waybill):
    return (f'Путевой лист <b>№{waybill.id}</b>\n'
            f'Дата: <u>{waybill.date[:10]}</u>\n'
            f'Продолжительность: {waybill.duration}ч\n'
            f'Гос.номер: {waybill.govNumber}\n'
            f'Значение одометра в конце: {waybill.mileageEnd}\n'
            f'Значение одометра на старте: {waybill.mileageStart}\n'
            f'Тип техники: {waybill.typeM}')


def print_task(task):
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

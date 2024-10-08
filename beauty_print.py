def print_CalendarTask(CalendarTask):
    return (f'Задание <b>№{CalendarTask.id}</b>\n'
          f"Дата: <u>{CalendarTask.calendarDate[:10]}</u>\n"
          f'Продолжительность: {CalendarTask.calendarDuration}ч\n'
          f'Время начала работы: <u>{CalendarTask.calendarDate[:10]}</u>\n'
          f'Наименование техники: {CalendarTask.machine}\n')


def print_Waybill(Waybill):
    return (f'Путевой лист <b>№{Waybill.id}</b>\n'
            f'Дата: <u>{Waybill.date[:10]}</u>\n'
            f'Продолжительность: {Waybill.duration}ч\n'
            f'Гос.номер: {Waybill.govNumber}\n'
            f'Значение одометра в конце: {Waybill.mileageEnd}\n'
            f'Значение одометра на старте: {Waybill.mileageStart}\n'
            f'Тип техники: {Waybill.typeM}')

def print_Task(Task):
    return(f'Задание <b>№{Task.id}</b>\n'
           f'Заказчик: {Task.order}\n'
           f'Время прибытия: <u>{Task.arrivalTime}</u>\n'
           f'Адрес погрузки: {Task.loadingAddress}\n'
           f'Адресс разгрузки: {Task.unloadingAddress}\n'
           f'Наименование груза: {Task.cargoName}\n'
           f'Количество ездок: {Task.count}\n'
           f'Расстояние: {Task.distance} км\n'
           f'Перевезти: {Task.transported} тонн\n'
           f'Примечание {Task.description}')

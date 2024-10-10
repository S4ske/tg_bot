from aiogram.fsm.state import StatesGroup, State


class Credentials(StatesGroup):
    login = State()
    password = State()


class Menu(StatesGroup):
    main = State()
    checking_waybills = State()
    waybill = State()
    checking_checklists = State()
    accepting_checklist = State()
    checklist = State()
    starting_work = State()
    stopping_work = State()
    checking_tasks = State()
    task = State()
    deleting_result = State()
    entering_time = State()
    entering_distance = State()
    entering_transported = State()

from pydantic import BaseModel
from typing import TypeVar, Generic
from enum import Enum
from aiogram.fsm.state import State, StatesGroup

T = TypeVar('T')


class Credentials(StatesGroup):
    login = State()
    password = State()


class Menu(StatesGroup):
    main = State()
    checking_waybill = State()
    waybill = State()


class AnswerType(Enum):
    checkbox = 1
    button = 2
    text = 3


class DefaultResponse(BaseModel):
    success: bool


class LoginResponse(DefaultResponse):
    token: str | None = None


class ResponseWithGet(DefaultResponse, Generic[T]):
    get: T | None = None


class UserInfo(BaseModel):
    avatar: int | None
    avatarName: str | None
    chapter: str | None
    login: str | None
    name: str | None
    patronymic: str | None
    surname: str | None


class CalendarTask(BaseModel):
    '''
    Attributes:
        calendarDate: дата
        calendarDuration: продолжительность в часах
        calendarTime: начало работы время, example: 07:00: 00
        id
        idWaybill: id путевого листа
        link: ссылка для доступа к путевому листу
        machine: наименование техники
        pswd: пароль для доступу к путевому листу
    '''
    calendarDate: str | None
    calendarDuration: int | None
    calendarTime: str | None
    id: int | None
    idWaybill: int | None
    link: str | None
    machine: str | None
    pswd: str | None


class Waybill(BaseModel):
    '''
    Attributes:
        date
        dateEnd
        dateStart
        duration: продолжительность в часах
        govNumber: гос номер
        id
        idMachine: id техники
        mileageEnd: Значение одометра в конце
        mileageStart: Значение одометра на старте
        model: наименование техники
        time: начало работы время, example: 07:00:00
        typeM: тип техники
    '''
    date: str | None
    dateEnd: str | None
    dateStart: str | None
    duration: int | None
    govNumber: str | None
    id: int | None
    idMachine: int | None
    mileageEnd: int | None
    mileageStart: int | None
    model: str | None
    time: str | None
    typeM: str | None


class Checklist(BaseModel):
    '''
    Attributes:
        checklistWaybillId
        dateFinish: дата завершения теста, если тест пройден иначе null
        id
        name
    '''
    checklistWaybillId: int | None
    dateFinish: str | None
    id: int | None
    name: str | None


class Button(BaseModel):
    name: str | None


class AnswerParam(BaseModel):
    buttonNumber: int | None
    buttonArr: list[Button] | None


class Question(BaseModel):
    id: int | None
    questionNumber: int | None
    question: str | None
    description: str | None
    answerType: AnswerType | None
    answerParam: AnswerParam | None
    idAnswer: int | None
    answer: str | None


class IntermediateTaskResult(BaseModel):
    arrivalTime: str | None
    count: str | None
    distance: str | None
    id: int | None
    transported: str | None


class Task(BaseModel):
    id: int | None
    order: str | None
    arrivalTime: str | None
    loadingAddress: str | None
    unloadingAddress: str | None
    cargoName: str | None
    count: str | None
    distance: str | None
    transported: str | None
    isFinished: bool | None
    dateFinished: str | None
    typeWork: str | None
    description: str | None
    taskResult: list[IntermediateTaskResult] | None


class TaskResult(BaseModel):
    id: int | None
    idTask: int | None
    order: str | None
    arrivalTime: str | None
    loadingAddress: str | None
    unloadingAddress: str | None
    cargoName: str | None
    isFinished: bool | None
    dateFinished: str | None
    count: str | None
    distance: str | None
    transported: str | None
    arrivalTimeResult: str | None
    countResult: str | None
    distanceResult: str | None
    transportedResult: str | None


class DriverResponse(ResponseWithGet[list[CalendarTask]]):
    count: int | None
    current: list[CalendarTask] | None

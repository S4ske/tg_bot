from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from states import Menu
from aiogram.fsm.context import FSMContext
from schemas import Waybill, Checklist, Question, AnswerType
from api import API
from utils import get_keyboard_markup_checklists, waybill_markup, get_keyboard_markup_buttons, checkbox_markup, \
    default_checklist_markup, validate_response
from beauty_print import print_checklist

router = Router()


@router.message(Menu.checking_checklists, F.text.casefold() == 'назад')
@router.message(Menu.accepting_checklist, F.text.casefold() == 'назад')
@router.message(Menu.checklist, F.text.casefold() == 'покинуть контрольный лист')
async def back(message: Message, state: FSMContext):
    await state.set_state(Menu.waybill)
    await message.answer('Возвращение...', reply_markup=waybill_markup)


@router.message(Menu.checklist, F.text.casefold() == 'назад')
async def back_checklist(message: Message, state: FSMContext):
    data = await state.get_data()
    question_num = int(data['question_num'])
    if question_num == 0:
        await back(message, state)
    else:
        question_num -= 1
        await state.update_data(question_num=question_num)
        questions = list(map(lambda x: Question(**x), data['questions']))
        current_question = questions[question_num]
        if current_question.answerType == AnswerType.checkbox:
            await message.answer(current_question.question, reply_markup=checkbox_markup)
        elif current_question.answerType == AnswerType.button:
            await message.answer(current_question.question,
                                 reply_markup=get_keyboard_markup_buttons(current_question.answerParam.buttonArr))
        else:
            await message.answer(current_question.question, reply_markup=default_checklist_markup)


@router.message(Menu.waybill, F.text.casefold() == 'контрольные листы')
async def get_checklists(message: Message, state: FSMContext):
    data = await state.get_data()
    token = data['token']
    waybill = Waybill(**data['waybill'])
    checklists_resp = await API.get_checklists(token, waybill.id)
    if not await validate_response(message, checklists_resp):
        return
    checklists = checklists_resp.get
    await message.answer(f'Контрольные листы для путевого листа "{waybill.govNumber} <u>{waybill.date[:10]}":</u>',
                         reply_markup=get_keyboard_markup_checklists(checklists))
    for checklist in checklists:
        await message.answer(print_checklist(checklist))
    await state.set_state(Menu.checking_checklists)


@router.message(Menu.checking_checklists)
async def get_questions(message: Message, state: FSMContext):
    data = await state.get_data()
    token = data['token']
    waybill = Waybill(**data['waybill'])
    checklists_resp = await API.get_checklists(token, waybill.id)
    try:
        checklist = list(filter(lambda x: x.checklistWaybillId == int(message.text), checklists_resp.get))[0]
    except:
        await message.answer('Введите номер существующего контрольного листа')
        return
    await message.answer(f'Вы готовы к прохождению контролього листа "{checklist.name}"?',
                         reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Начать')],
                                                                    [KeyboardButton(text='Назад')]]))
    await state.update_data(checklist=checklist.model_dump())
    await state.set_state(Menu.accepting_checklist)


async def validate_answer(message: Message, state: FSMContext, current_question) -> bool:
    data = await state.get_data()
    token = data['token']
    waybill = Waybill(**data['waybill'])
    checklist = Checklist(**data['checklist'])
    if current_question.answerType == AnswerType.checkbox and message.text.casefold() not in ['да', 'нет']:
        await message.answer('Введите Да/Нет')
        return False
    elif current_question.answerType == AnswerType.button \
            and message.text not in list(map(lambda x: x.name, current_question.answerParam.buttonArr)):
        await message.answer('Данного ответа нет в списке')
        return False
    answer_resp = await API.put_checklist_answer(token, waybill.id, checklist.checklistWaybillId,
                                                 message.text, current_question.id)
    return await validate_response(message, answer_resp)


async def ask_question(message: Message, question: Question) -> None:
    if question.answerType == AnswerType.checkbox:
        await message.answer(question.question, reply_markup=checkbox_markup)
    elif question.answerType == AnswerType.button:
        await message.answer(question.question,
                             reply_markup=get_keyboard_markup_buttons(question.answerParam.buttonArr))
    else:
        await message.answer(question.question, reply_markup=default_checklist_markup)
        await message.answer('Введите значение')


async def start_checklist(message: Message, state: FSMContext) -> bool:
    data = await state.get_data()
    token = data['token']
    waybill = Waybill(**data['waybill'])
    checklist = Checklist(**data['checklist'])
    if not checklist.checklistWaybillId:
        start_resp = await API.start_checklist(token, waybill.id, checklist.id)
        if not await validate_response(message, start_resp):
            return False
        checklist.checklistWaybillId = start_resp.get
        await state.update_data(checklist=checklist)
    questions_resp = await API.get_checklist_questions(token, waybill.id, checklist.checklistWaybillId)
    questions = questions_resp.get
    questions_dump = list(map(lambda x: x.model_dump(), questions))
    await state.update_data(questions=questions_dump)
    question_num = 0
    await state.update_data(question_num=question_num)
    await state.set_state(Menu.checklist)
    return True


async def stop_checklist(message: Message, state: FSMContext) -> bool:
    data = await state.get_data()
    token = data['token']
    waybill = Waybill(**data['waybill'])
    checklist = Checklist(**data['checklist'])
    stop_resp = await API.stop_checklist(token, waybill.id, checklist.checklistWaybillId)
    if not await validate_response(message, stop_resp):
        return False
    await message.answer('Ответы сохранены', reply_markup=waybill_markup)
    await state.set_state(Menu.waybill)
    return True


@router.message(Menu.accepting_checklist, F.text.casefold() == 'начать')
@router.message(Menu.checklist)
async def accept_checklist(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == 'Menu:accepting_checklist':
        if not await start_checklist(message, state):
            return
        data = await state.get_data()
        question_num = int(data['question_num'])
        questions = list(map(lambda x: Question(**x), data['questions']))
    else:
        data = await state.get_data()
        question_num = int(data['question_num'])
        questions = list(map(lambda x: Question(**x), data['questions']))
        current_question = questions[question_num]
        if not await validate_answer(message, state, current_question):
            return
        question_num += 1
        await state.update_data(question_num=question_num)
    if question_num > len(questions) - 1:
        if not await stop_checklist(message, state):
            return
    else:
        current_question = questions[question_num]
        await ask_question(message, current_question)

import pytest
from unittest.mock import AsyncMock, patch, Mock
from aiogram.types import ReplyKeyboardRemove
import telegram.main
from telegram.routers import auth, checklist, tasks, title, waybill
from src.dto import states, schemas
from telegram.keyboards import main_keyboard_markup, task_markup, waybill_markup


class TestMessageHandlers:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.state = AsyncMock()
        self.message = AsyncMock()

    @pytest.fixture
    def setup_token(self):
        self.state.get_data.return_value = {"token": ""}

    @pytest.fixture
    def setup_waybill(self):
        self.fake_waybill_dict = {
            "date": "000000000000",
            "dateEnd": None,
            "dateStart": None,
            "duration": None,
            "govNumber": "0",
            "id": None,
            "idMachine": None,
            "mileageEnd": None,
            "mileageStart": None,
            "model": None,
            "time": None,
            "typeM": None,
        }
        self.state.get_data.return_value = {
            "token": "",
            "waybill": self.fake_waybill_dict,
        }

    async def _message_handler_test_base(
        self, handler, answer_text=None, new_markup=None
    ):
        await handler(self.message, self.state)

        if answer_text:
            if new_markup:
                self.message.answer.assert_called_once_with(
                    answer_text, reply_markup=new_markup
                )
            else:
                calls = self.message.answer.call_args_list
                assert len(calls) == 1
                assert calls[0][0][0] == answer_text

    async def _message_handler_test(
        self, handler, new_state=None, answer_text=None, new_markup=None
    ):
        await self._message_handler_test_base(handler, answer_text, new_markup)

        if new_state:
            self.state.set_state.assert_called_once_with(new_state)

    async def _message_handler_test_with_clear_state(
        self, handler, answer_text=None, new_markup=None
    ):
        await self._message_handler_test_base(handler, answer_text, new_markup)

        self.state.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_bot(self):
        await self._message_handler_test(
            telegram.main.start,
            new_state=states.Credentials.login,
            answer_text="Привет! Отправь мне свой логин",
            new_markup=ReplyKeyboardRemove(),
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "original_state, answer_text, new_state, new_markup",
        [
            ("Credentials:login", "Вы не авторизованы", None, None),
            ("some_unexpected_state", "Вы не авторизованы", None, None),
            ("Menu:main", "Возвращение...", states.Menu.main, main_keyboard_markup),
            (
                "Menu:some_page",
                "Возвращение...",
                states.Menu.main,
                main_keyboard_markup,
            ),
        ],
    )
    async def test_to_main_menu(
        self, original_state: str, answer_text: str, new_state, new_markup
    ):
        self.state.get_state.return_value = original_state
        await self._message_handler_test(
            telegram.main.to_main_menu,
            new_state=new_state,
            answer_text=answer_text,
            new_markup=new_markup,
        )

    @pytest.mark.asyncio
    async def test_login(self):
        await self._message_handler_test(
            auth.login,
            answer_text="Отлично, теперь отправь свой пароль",
            new_state=states.Credentials.password,
            new_markup=ReplyKeyboardRemove(),
        )

    @pytest.mark.asyncio
    @patch("src.api.API.login")
    @pytest.mark.parametrize(
        "login_response, is_valid",
        {
            (Mock(schemas.LoginResponse, success=True, token="example"), True),
            (Mock(schemas.LoginResponse, success=False, token="example"), False),
            (None, False),
        },
    )
    async def test_check_password(
        self, mock, login_response: schemas.LoginResponse, is_valid: bool
    ):
        self.state.get_data.return_value = {"login": "", "password": ""}
        mock.return_value = login_response
        if is_valid:
            await self._message_handler_test(
                auth.check_password,
                new_state=states.Menu.main,
                new_markup=main_keyboard_markup,
                answer_text="Вы успешно авторизировались",
            )
        else:
            await self._message_handler_test_with_clear_state(
                auth.check_password,
                new_markup=None,
                answer_text="Неправильный логин или пароль",
            )

    @pytest.mark.asyncio
    async def test_logout(self):
        await self._message_handler_test_with_clear_state(
            auth.logout,
            answer_text="Вы успешно вышли",
            new_markup=ReplyKeyboardRemove(),
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "get_checklists_response, new_state, answer_text",
        [
            (
                Mock(
                    schemas.ResponseWithGet,
                    success=True,
                    get=[Mock(schemas.Checklist, id=1)],
                ),
                states.Menu.checking_checklists,
                None,
            ),
            (None, None, "Что-то пошло не так"),
            (Mock(schemas.ResponseWithGet, success=False), None, "Что-то пошло не так"),
        ],
    )
    @patch("src.api.API.get_checklists")
    @patch("telegram.routers.checklist.print_checklist")
    async def test_get_checklists(
        self,
        mock_print,
        mock_api,
        get_checklists_response,
        new_state,
        answer_text,
        setup_waybill,
    ):
        mock_api.return_value = get_checklists_response
        mock_print.return_value = ""
        if new_state:
            await self._message_handler_test(
                checklist.get_checklists, new_state=new_state
            )
            self.message.answer.assert_called()
        elif answer_text:
            await self._message_handler_test_base(
                checklist.get_checklists, answer_text=answer_text
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "get_tasks_response, new_state, answer_text",
        [
            (None, None, "Что-то пошло не так"),
            (Mock(schemas.TaskResponse, success=False), None, "Что-то пошло не так"),
            (
                Mock(
                    schemas.TaskResponse,
                    success=True,
                    task=[
                        Mock(schemas.TaskResult, id=1),
                        Mock(schemas.TaskResult, id=2),
                    ],
                ),
                states.Menu.checking_tasks,
                None,
            ),
        ],
    )
    @patch("src.api.API.get_tasks")
    @patch("telegram.routers.tasks.print_task")
    async def test_get_tasks(
        self,
        mock_print,
        mock_api,
        get_tasks_response,
        new_state,
        answer_text,
        setup_waybill,
    ):
        mock_api.return_value = get_tasks_response
        mock_print.return_value = ""
        await self._message_handler_test(
            tasks.get_tasks, new_state=new_state, answer_text=answer_text
        )
        if not answer_text:
            self.message.answer.assert_called()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "get_tasks_response, message_text, answer_text, new_state, new_markup",
        [
            (
                Mock(schemas.TaskResult, success=False),
                None,
                "Что-то пошло не так",
                None,
                None,
            ),
            (None, None, "Что-то пошло не так", None, None),
            (
                Mock(
                    schemas.TaskResult,
                    success=True,
                    task=[
                        Mock(schemas.TaskResult, id=1),
                        Mock(schemas.TaskResult, id=2),
                    ],
                ),
                "1",
                None,
                states.Menu.task,
                task_markup,
            ),
            (
                Mock(
                    schemas.TaskResult,
                    success=True,
                    task=[
                        Mock(schemas.TaskResult, id=1),
                        Mock(schemas.TaskResult, id=2),
                    ],
                ),
                "3",
                "Введите номер существующей задачи",
                None,
                None,
            ),
        ],
    )
    @patch("src.api.API.get_tasks")
    async def test_check_task(
        self,
        mock_api,
        get_tasks_response,
        message_text,
        answer_text,
        new_state,
        new_markup,
        setup_waybill,
    ):
        mock_api.return_value = get_tasks_response
        self.message.text = message_text
        await self._message_handler_test(
            tasks.check_task,
            answer_text=answer_text,
            new_state=new_state,
            new_markup=new_markup,
        )
        if not message_text:
            self.message.answer.assert_called()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "get_calendar_tasks_response, new_state, answer_text,",
        [
            (Mock(schemas.DriverResponse, success=False), None, "Что-то пошло не так"),
            (None, None, "Что-то пошло не так"),
            (
                Mock(
                    schemas.DriverResponse,
                    success=True,
                    get=[Mock(schemas.CalendarTask, idWaybill=1, id=1)],
                ),
                states.Menu.checking_waybills,
                None,
            ),
            (
                Mock(schemas.DriverResponse, success=True, get=[]),
                None,
                "<b>У вас нет заданий</b>",
            ),
        ],
    )
    @patch("src.api.API.get_calendar_tasks")
    @patch("telegram.routers.title.print_calendar_task")
    async def test_get_calendar_tasks(
        self,
        mock_print,
        mock_api,
        get_calendar_tasks_response,
        new_state,
        answer_text,
        setup_token,
    ):
        mock_api.return_value = get_calendar_tasks_response
        mock_print.return_value = ""
        await self._message_handler_test(
            title.get_calendar_tasks, new_state=new_state, answer_text=answer_text
        )
        if not answer_text:
            self.message.answer.assert_called()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "get_calendar_tasks_response, new_state, answer_text,",
        [
            (
                Mock(
                    schemas.ResponseWithGet[list[schemas.CalendarTask]], success=False
                ),
                None,
                "Что-то пошло не так",
            ),
            (None, None, "Что-то пошло не так"),
            (
                Mock(
                    schemas.ResponseWithGet[list[schemas.CalendarTask]],
                    success=True,
                    get=[Mock(schemas.CalendarTask, idWaybill=1, id=1)],
                ),
                states.Menu.checking_waybills,
                None,
            ),
            (
                Mock(
                    schemas.ResponseWithGet[list[schemas.CalendarTask]],
                    success=True,
                    get=[],
                ),
                None,
                "<b>У вас нет заданий на сегодня</b>",
            ),
        ],
    )
    @patch("src.api.API.get_current_calendar_tasks")
    @patch("telegram.routers.title.print_calendar_task")
    async def test_get_current_calendar_tasks(
        self,
        mock_print,
        mock_api,
        get_calendar_tasks_response,
        new_state,
        answer_text,
        setup_token,
    ):
        mock_api.return_value = get_calendar_tasks_response
        mock_print.return_value = ""
        await self._message_handler_test(
            title.get_current_calendar_tasks,
            new_state=new_state,
            answer_text=answer_text,
        )
        if not answer_text:
            self.message.answer.assert_called()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "get_calendar_tasks_response, message_text, new_state, answer_text, new_markup,"
        " get_waybill_response",
        [
            (
                Mock(schemas.DriverResponse, success=False),
                None,
                None,
                "Что-то пошло не так",
                None,
                None,
            ),
            (None, None, None, "Что-то пошло не так", None, None),
            (
                Mock(
                    schemas.DriverResponse,
                    success=True,
                    get=[Mock(schemas.CalendarTask, id=1, idWaybill=1)],
                ),
                "2",
                None,
                "Введите номер существующего задания",
                None,
                None,
            ),
            (
                Mock(
                    schemas.DriverResponse,
                    success=True,
                    get=[Mock(schemas.CalendarTask, id=1, idWaybill=None)],
                ),
                "1",
                None,
                "У этого задания нет путевого листа",
                None,
                None,
            ),
            (
                Mock(
                    schemas.DriverResponse,
                    success=True,
                    get=[Mock(schemas.CalendarTask, id=1, idWaybill=1)],
                ),
                "1",
                states.Menu.waybill,
                "Вы выбрали задание №1",
                waybill_markup,
                Mock(
                    schemas.ResponseWithGet[schemas.Waybill], success=True, get=Mock()
                ),
            ),
            (
                Mock(
                    schemas.DriverResponse,
                    success=True,
                    get=[Mock(schemas.CalendarTask, id=1, idWaybill=1)],
                ),
                "1",
                None,
                "Что-то пошло не так",
                None,
                Mock(schemas.ResponseWithGet[schemas.Waybill], success=False),
            ),
        ],
    )
    @patch("src.api.API.get_calendar_tasks")
    @patch("src.api.API.get_waybill")
    async def test_select_waybill(
        self,
        mock_waybill,
        mock_tasks,
        get_calendar_tasks_response,
        message_text,
        new_state,
        answer_text,
        new_markup,
        get_waybill_response,
        setup_token,
    ):
        self.message.text = message_text
        mock_tasks.return_value = get_calendar_tasks_response
        mock_waybill.return_value = get_waybill_response
        await self._message_handler_test(
            waybill.select_waybill,
            new_state=new_state,
            answer_text=answer_text,
            new_markup=new_markup,
        )

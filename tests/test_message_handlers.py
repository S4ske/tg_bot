import pytest
from unittest.mock import AsyncMock, patch, Mock
from aiogram.types import ReplyKeyboardRemove
import telegram.main
from telegram.routers import auth, checklist
from src.dto import states
from telegram.keyboards import main_keyboard_markup
from src.dto import schemas


class TestMessageHandlers:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.state = AsyncMock()
        self.message = AsyncMock()

    @pytest.fixture
    def setup_waybill(self):
        self.fake_waybill_dict = {"date": "000000000000", "dateEnd": None, "dateStart": None, "duration": None,
                                  "govNumber": "0", "id": None, "idMachine": None, "mileageEnd": None,
                                  "mileageStart": None, "model": None, "time": None, "typeM": None}

    async def message_handler_test_base(self, handler, answer_text=None, new_markup=None):
        assert not (not answer_text and new_markup)

        await handler(self.message, self.state)

        if answer_text:
            if new_markup:
                self.message.answer.assert_called_once_with(answer_text, reply_markup=new_markup)
            else:
                calls = self.message.answer.call_args_list
                assert len(calls) == 1
                assert calls[0][0][0] == answer_text

    async def message_handler_test(self, handler, new_state=None, answer_text=None, new_markup=None):
        await self.message_handler_test_base(handler, answer_text, new_markup)

        if new_state:
            self.state.set_state.assert_called_once_with(new_state)

    async def message_handler_test_with_clear_state(self, handler, answer_text=None, new_markup=None):
        await self.message_handler_test_base(handler, answer_text, new_markup)

        self.state.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_bot(self):
        await self.message_handler_test(telegram.main.start, new_state=states.Credentials.login,
                                        answer_text="Привет! Отправь мне свой логин",
                                        new_markup=ReplyKeyboardRemove())

    @pytest.mark.asyncio
    @pytest.mark.parametrize("original_state, answer_text, new_state, new_markup", [
        ("Credentials:login", "Вы не авторизованы", None, None),
        ("some_unexpected_state", "Вы не авторизованы", None, None),
        ("Menu:main", "Возвращение...", states.Menu.main, main_keyboard_markup),
        ("Menu:some_page", "Возвращение...", states.Menu.main, main_keyboard_markup),
    ])
    async def test_to_main_menu(self, original_state: str, answer_text: str, new_state, new_markup):
        self.state.get_state.return_value = original_state
        await self.message_handler_test(telegram.main.to_main_menu, new_state=new_state, answer_text=answer_text,
                                        new_markup=new_markup)

    @pytest.mark.asyncio
    async def test_login(self):
        await self.message_handler_test(auth.login, answer_text="Отлично, теперь отправь свой пароль",
                                        new_state=states.Credentials.password, new_markup=ReplyKeyboardRemove())

    @pytest.mark.asyncio
    @patch("src.api.API.login")
    @pytest.mark.parametrize("login_response, is_valid", {
        (Mock(schemas.LoginResponse, success=True, token="example"), True),
        (Mock(schemas.LoginResponse, success=False, token="example"), False),
        (None, False),
    })
    async def test_check_password(self, mock, login_response: schemas.LoginResponse, is_valid: bool):
        self.state.get_data.return_value = {"login": "", "password": ""}
        mock.return_value = login_response
        if is_valid:
            await self.message_handler_test(auth.check_password, new_state=states.Menu.main,
                                            new_markup=main_keyboard_markup, answer_text="Вы успешно авторизировались")
        else:
            await self.message_handler_test_with_clear_state(auth.check_password, new_markup=None,
                                                             answer_text="Неправильный логин или пароль")

    @pytest.mark.asyncio
    async def test_logout(self):
        await self.message_handler_test_with_clear_state(auth.logout, answer_text="Вы успешно вышли",
                                                         new_markup=ReplyKeyboardRemove())

    @pytest.mark.asyncio
    @patch("src.api.API.get_checklists")
    @patch("telegram.beauty_print.print_checklist")
    @pytest.mark.parametrize("get_checklists_response, new_state, answer_text", [
        (Mock(schemas.ResponseWithGet, success=True, get=[Mock(schemas.Checklist, id=1)]),
         states.Menu.checking_checklists, None),
        (None, None, "Что-то пошло не так"),
        (Mock(schemas.ResponseWithGet, success=False), None, "Что-то пошло не так")
    ])
    async def test_get_checklists(self, get_checklists_response, new_state, answer_text, mock_print, mock_api,
                                  setup_waybill):
        self.state.get_data.return_value = {"token": "", "waybill": self.fake_waybill_dict}
        mock_api.return_value = get_checklists_response
        mock_print.return_value = ""
        if new_state:
            await self.message_handler_test(checklist.get_checklists, new_state=new_state)
            self.message.answer.called()
        elif answer_text:
            await self.message_handler_test_base(checklist.get_checklists, answer_text=answer_text)

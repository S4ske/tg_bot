import pytest
from src import utils
from unittest.mock import AsyncMock, Mock, patch
from src.dto.schemas import TaskResponse, Task


class TestUtils:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.message = AsyncMock()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("is_success, exception_message, result, answer_text", [
        (True, None, True, None),
        (False, None, False, "Что-то пошло не так"),
        (False, "example", False, "example"),
    ])
    async def test_validate_response_with_not_none(self, is_success: bool, exception_message: str | None,
                                                   result: bool, answer_text: str | None):
        response = Mock()
        response.success = is_success
        validation_res = await utils.validate_response(self.message, response, exception_message)
        assert validation_res == result
        if validation_res is False:
            self.message.answer.assert_called_once_with(answer_text)
        else:
            self.message.answer.assert_not_called()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("exception_message", [
        None,
        "example",
    ])
    async def test_validate_response_with_none(self, exception_message: str | None):
        validation_res = await utils.validate_response(self.message, None, exception_message)

        assert validation_res is False
        if exception_message:
            self.message.answer.assert_called_once_with(exception_message)
        else:
            self.message.answer.assert_called_once_with("Что-то пошло не так")

    @pytest.mark.asyncio
    @patch("src.api.API.get_tasks")
    @pytest.mark.parametrize("task_id, get_tasks_response, is_valid, contains", [
        (None, None, False, False),
        (1, Mock(TaskResponse, task=[Mock(Task, id=2), Mock(Task, id=1), Mock(Task, id=3)], success=True), True, True),
        (2, Mock(TaskResponse, task=[Mock(Task, id=1), Mock(Task, id=3)], success=True), True, False),
        (1337, Mock(TaskResponse, success=False), False, False)
    ])
    async def test_get_task_by_id(self, mock, task_id: int, get_tasks_response: TaskResponse, is_valid: bool,
                                  contains: bool):
        mock.return_value = get_tasks_response
        result = await utils.get_task_by_id(self.message, "doesn't_matter", 1337, task_id)
        if is_valid:
            if contains:
                assert result.id == task_id
            self.message.answer.assert_not_called()
        else:
            self.message.answer.assert_called_once_with("Что-то пошло не так")
            assert result is None

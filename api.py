from aiohttp import ClientSession
import schemas
from typing import Any, Callable, TypeVar, Type
from pydantic import BaseModel

T = TypeVar('T')


class RawResponse(BaseModel):
    status: int
    data: dict | None


class API:
    url = 'https://portal.skybuild.ru/api/1/app_worker'

    @staticmethod
    async def _get_return(response: RawResponse, schema: Type[T]) -> T | None:
        if str(response.status)[0] != '5':
            return schema(**response.data)
        else:
            return None

    @staticmethod
    async def _send_request(method: Callable, request: str, body: dict[str, Any] = None, headers: dict[str, Any] = None,
                            params: dict[str, Any] = None) -> RawResponse:
        body = body if body else dict()
        headers = headers if headers else dict()
        params = params if params else dict()
        async with ClientSession() as session:
            async with method(session, API.url + request, json=body, headers=headers, params=params) as response:
                return RawResponse(status=response.status, data=None if str(response.status)[0] == '5'
                else await response.json())

    @staticmethod
    async def send_get_request(request: str, body: dict[str, Any] = None, headers: dict[str, Any] = None,
                               params: dict[str, Any] = None) -> RawResponse:
        return await API._send_request(ClientSession.get, request, body, headers, params)

    @staticmethod
    async def send_post_request(request: str, body: dict[str, Any] = None, headers: dict[str, Any] = None,
                                params: dict[str, Any] = None) -> RawResponse:
        return await API._send_request(ClientSession.post, request, body, headers, params)

    @staticmethod
    async def send_put_request(request: str, body: dict[str, Any] = None, headers: dict[str, Any] = None,
                               params: dict[str, Any] = None) -> RawResponse:
        return await API._send_request(ClientSession.put, request, body, headers, params)

    @staticmethod
    async def login(login: str, password: str) -> schemas.LoginResponse | None:
        response = await API.send_post_request('/login', body={'login': login, 'password': password})
        return await API._get_return(response, schemas.LoginResponse)

    @staticmethod
    async def get_me(token: str) -> schemas.ResponseWithGet[schemas.UserInfo] | None:
        response = await API.send_get_request('/me', headers={'x-access-token': token})
        return await API._get_return(response, schemas.ResponseWithGet[schemas.UserInfo])

    @staticmethod
    async def get_calendar_tasks(token: str, limit: int | None = None, offset: int | None = None) \
            -> schemas.DriverResponse | None:
        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        response = await API.send_get_request('/driver', headers={'x-access-token': token}, params=params)
        return await API._get_return(response, schemas.DriverResponse)

    @staticmethod
    async def get_current_calendar_tasks(token: str) -> schemas.ResponseWithGet[list[schemas.CalendarTask]] | None:
        response = await API.send_get_request('/driver-current', headers={'x-access-token': token})
        return await API._get_return(response, schemas.ResponseWithGet[list[schemas.CalendarTask]])

    @staticmethod
    async def get_waybill(token: str, id_waybill: int) -> schemas.ResponseWithGet[schemas.Waybill] | None:
        response = await API.send_get_request(f'/waybill/{id_waybill}', headers={'x-access-token': token})
        return await API._get_return(response, schemas.ResponseWithGet[schemas.Waybill])

    @staticmethod
    async def start_waybill(token: str, id_waybill: int, mileage_start: int) -> schemas.DefaultResponse | None:
        response = await API.send_put_request(f'/waybill/{id_waybill}/start', headers={'x-access-token': token},
                                              body={'mileageStart': mileage_start})
        return await API._get_return(response, schemas.DefaultResponse)

    @staticmethod
    async def stop_waybill(token: str, id_waybill: int, mileage_end: int) -> schemas.DefaultResponse | None:
        response = await API.send_put_request(f'/waybill/{id_waybill}/stop', headers={'x-access-token': token},
                                              body={'mileageStart': mileage_end})
        return await API._get_return(response, schemas.DefaultResponse)

    @staticmethod
    async def get_checklists(token: str, id_waybill: int) -> schemas.ResponseWithGet[list[schemas.Checklist]] | None:
        response = await API.send_get_request(f'/waybill/{id_waybill}/c_list', headers={'x-access-token': token})
        return await API._get_return(response, schemas.ResponseWithGet[list[schemas.Checklist]])

    @staticmethod
    async def get_checklist_questions(token: str, id_waybill: int, id_ChWB: int) \
            -> schemas.ResponseWithGet[list[schemas.Question]] | None:
        response = await API.send_get_request(f'/waybill/{id_waybill}/c_list/{id_ChWB}',
                                              headers={'x-access-token': token})
        return await API._get_return(response, schemas.ResponseWithGet[list[schemas.Question]])

    @staticmethod
    async def start_checklist(token: str, id_waybill: int, id_ChWB: int) -> schemas.ResponseWithGet[int] | None:
        response = await API.send_post_request(f'/waybill/{id_waybill}/c_list/{id_ChWB}/start',
                                               headers={'x-access-token': token})
        return await API._get_return(response, schemas.ResponseWithGet[int])

    @staticmethod
    async def put_checklist_answer(token: str, id_waybill: int, id_ChWB: int, answer: str, question_id: int) \
            -> schemas.DefaultResponse | None:
        response = await API.send_put_request(f'/waybill/{id_waybill}/c_list/{id_ChWB}/answer',
                                              headers={'x-access-token': token},
                                              body={'answer': answer, 'questionId': question_id})
        return await API._get_return(response, schemas.DefaultResponse)

    @staticmethod
    async def stop_checklist(token: str, id_waybill: int, id_ChWB: int) -> schemas.DefaultResponse | None:
        response = await API.send_put_request(f'/waybill/{id_waybill}/c_list/{id_ChWB}/stop',
                                              headers={'x-access-token': token})
        return await API._get_return(response, schemas.DefaultResponse)

    @staticmethod
    async def get_tasks(token: str, id_waybill: int) -> schemas.TaskResponse | None:
        response = await API.send_get_request(f'/waybill/{id_waybill}/task', headers={'x-access-token': token})
        return await API._get_return(response, schemas.TaskResponse)

    @staticmethod
    async def add_task_result(token: str, id_waybill: int, result: schemas.IntermediateTaskResultIn)\
            -> schemas.DefaultResponse | None:
        response = await API.send_put_request(f'/waybill/{id_waybill}/task_result', headers={'x-access-token': token},
                                              body=result.model_dump())
        return await API._get_return(response, schemas.DefaultResponse)

    @staticmethod
    async def remove_task_result(token: str, id_waybill: int, id_task_result: int) -> schemas.DefaultResponse | None:
        response = await API.send_put_request(f'/waybill/{id_waybill}/task_result_remove',
                                              headers={'x-access-token': token}, body={'idTaskResult': id_task_result})
        return await API._get_return(response, schemas.DefaultResponse)

    @staticmethod
    async def stop_continue_task(token: str, id_waybill: int, id_task: int, is_finished: bool)\
            -> schemas.DefaultResponse | None:
        response = await API.send_put_request(f'/waybill/{id_waybill}/task_finish', headers={'x-access-token': token},
                                              body={'idTask': id_task, 'isFinished': is_finished})
        return await API._get_return(response, schemas.DefaultResponse)

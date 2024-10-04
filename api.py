from aiohttp import ClientSession
import schemas


class API:
    url = 'https://portal.skybuild.ru/api/1/app_worker'

    @staticmethod
    async def login(login: str, password: str) -> schemas.LoginResponse | None:
        async with ClientSession() as session:
            async with session.post('https://portal.skybuild.ru/api/1/app_worker/login',
                                    json={'login': login, 'password': password}) as response:
                if str(response.status)[0] != '5':
                    return schemas.LoginResponse(**await response.json())
                else:
                    return None

    @staticmethod
    async def get_me(token: str) -> schemas.ResponseWithGet[schemas.UserInfo] | None:
        async with ClientSession() as session:
            async with session.get('https://portal.skybuild.ru/api/1/app_worker/me',
                                   headers={'x-access-token': token}) as response:
                if str(response.status)[0] != '5':
                    return schemas.ResponseWithGet[schemas.UserInfo](**await response.json())
                else:
                    return None

    @staticmethod
    async def get_calendar_tasks(token: str, limit: int | None = None, offset: int | None = None)\
            -> schemas.DriverResponse | None:
        async with ClientSession() as session:
            params = {}
            if limit:
                params['limit'] = limit
            if offset:
                params['offset'] = offset
            async with session.get('https://portal.skybuild.ru/api/1/app_worker/driver',
                                   headers={'x-access-token': token}, params=params) as response:
                if str(response.status)[0] != '5':
                    return schemas.DriverResponse(**await response.json())
                else:
                    return None

    @staticmethod
    async def get_current_calendar_tasks(token: str) -> schemas.ResponseWithGet[list[schemas.CalendarTask]] | None:
        async with ClientSession() as session:
            async with session.get('https://portal.skybuild.ru/api/1/app_worker/driver-current',
                                   headers={'x-access-token': token}) as response:
                if str(response.status)[0] != '5':
                    return schemas.ResponseWithGet[list[schemas.CalendarTask]](**await response.json())
                else:
                    return None

    @staticmethod
    async def get_waybill(token: str, id_waybill: int) -> schemas.ResponseWithGet[schemas.Waybill] | None:
        async with ClientSession() as session:
            async with session.get('https://portal.skybuild.ru/api/1/app_worker/waybill/{}'.format(id_waybill),
                                   headers={'x-access-token': token}) as response:
                if str(response.status)[0] != '5':
                    return schemas.ResponseWithGet[schemas.Waybill](**await response.json())
                else:
                    return None

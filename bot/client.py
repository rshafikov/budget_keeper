import functools
import logging
from http import HTTPStatus

import aiohttp
from aiohttp.client_exceptions import ClientError
from decouple import config

from api.schemas.user_schemas import UserSecure, UserUpdate

_PASSWORD = config('API_PASSWORD')


logger = logging.getLogger(__name__)


def log_http_requests(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger.debug('C -> S: %r = %s', func.__name__, kwargs)
        try:
            response = await func(*args, **kwargs)
            logger.debug('S -> C: %r = %s', func.__name__, response)
            return response
        except AttributeError as e:
            logger.error('%r request handling failed: %s', func.__name__, e)

        except ClientError as e:
            logger.error('%r request proccessing failed: %s', func.__name__, e)

        except Exception as e:
            logger.error('%r unknown error: %s', func.__name__, e)

        return None

    return wrapper


class APIClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    @staticmethod
    def _get_headers(token: str | bytes) -> dict[str, str]:
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    @log_http_requests
    async def create_user(
            self,
            telegram_id: int,
            name: str | None = None,
            lastname: str | None = None
    ) -> dict[str, str]:
        payload = {
            "telegram_id": str(telegram_id),
            "password": _PASSWORD,
            "name": name,
            "lastname": lastname
        }
        async with self.session.post("/api/v1/users/", json=payload) as response:
            user = await response.json()
            return user if response.status == HTTPStatus.CREATED else None

    @log_http_requests
    async def get_users(self, token: str, offset: int = 0, limit: int = 100):
        params = {'offset': offset, 'limit': limit}
        headers = self._get_headers(token)
        async with self.session.get("/api/v1/users/", headers=headers, params=params) as response:
            return await response.json()

    @log_http_requests
    async def get_user(self, token: str, tg_id: str):
        headers = self._get_headers(token)
        async with self.session.get(f"/api/v1/users/{tg_id}/", headers=headers) as response:
            return await response.json()

    @log_http_requests
    async def user_profile(self, token: str):
        headers = self._get_headers(token)
        async with self.session.get("/api/v1/users/me", headers=headers) as response:
            return await response.json()

    @log_http_requests
    async def update_user(
            self,
            token: str,
            name: str | None = None,
            lastname: str | None = None,
            currency: str | None = None
    ) -> UserSecure:
        user_upd = UserUpdate(name=name, lastname=lastname, currency=currency)
        payload = user_upd.model_dump(exclude_none=True)
        headers = self._get_headers(token)

        async with self.session.put("/api/v1/users/me", headers=headers, json=payload) as response:
            upd = await response.json()
            return UserSecure.model_validate(upd)

    @log_http_requests
    async def get_categories(self, token: str, hidden: bool | None = None):
        params = {'hidden': hidden}
        headers = self._get_headers(token)
        async with self.session.get(
                "/api/v1/categories/", headers=headers, params=params
        ) as response:
            return await response.json()

    @log_http_requests
    async def create_category(self, token: str, name: str, symbol: str | None = None):
        payload = {"name": name, "symbol": symbol}
        headers = self._get_headers(token)
        async with self.session.post(
                "/api/v1/categories/", headers=headers, json=payload
        ) as response:
            return await response.json()

    @log_http_requests
    async def update_category(
            self,
            token: str,
            category_name: str,
            name: str | None = None,
            symbol: str | None = None
    ):
        payload = {"name": name, "symbol": symbol}
        headers = self._get_headers(token)
        async with self.session.put(
                f"/api/v1/categories/{category_name}", headers=headers, json=payload
        ) as response:
            return await response.json()

    @log_http_requests
    async def delete_category(self, token: str, category_name: str):
        headers = self._get_headers(token)
        async with self.session.delete(
                f"/api/v1/categories/{category_name}", headers=headers
        ) as response:
            return response.status == 204

    @log_http_requests
    async def create_currency(self, token: str, name: str, symbol: str | None = None):
        payload = {"name": name, "symbol": symbol}
        headers = self._get_headers(token)

        async with self.session.post(
                "/api/v1/currency/", headers=headers, json=payload
        ) as response:
            return await response.json()

    @log_http_requests
    async def get_currency(self, token: str, currency_name: str):
        headers = self._get_headers(token)
        async with self.session.get(f"currency/{currency_name}/", headers=headers) as response:
            return await response.json()

    @log_http_requests
    async def get_records(
            self,
            token: str,
            from_date: str | None = None,
            to_date: str | None = None
    ):
        params = {'from': from_date, 'to': to_date}
        headers = self._get_headers(token)
        async with self.session.get(
                "/api/v1/records/", headers=headers, params=params
        ) as response:
            return await response.json()

    @log_http_requests
    async def create_record(
            self,
            token: str,
            amount: float,
            category_name: str,
            currency: str | None = None
    ):
        payload = {"amount": amount, "category_name": category_name}
        params = {"currency": currency}
        headers = self._get_headers(token)
        async with self.session.post(
                "/api/v1/records/", headers=headers, json=payload, params=params
        ) as response:
            return await response.json()

    @log_http_requests
    async def get_token(
            self,
            telegram_id: int,
            client_id: str | None = None,
            client_secret: str | None = None,
            scope: str | None = None
    ) -> str:
        data = {
            "grant_type": "password",
            "username": str(telegram_id),
            "password": _PASSWORD,
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        async with self.session.post("/api/v1/auth/token", headers=headers, data=data) as response:
            response = await response.json()
            return response.get('access_token')

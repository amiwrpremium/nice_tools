import typing as t
from abc import ABC, abstractmethod

import json

import requests
import aiohttp
import asyncio


__all__ = [
    'BaseClient',
]


class APIException(Exception):
    def __init__(self, response: t.Union[requests.Response, aiohttp.ClientResponse], status_code: int, text: str):
        self.code = 0

        try:
            json_res = json.loads(text)
        except ValueError:
            self.message = 'Invalid JSON error message from Site: {}'.format(response.text)
        else:
            self.code = json_res['code']
            self.message = json_res['message']
            self.result = json_res['result']

        self.status_code = status_code
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):  # pragma: no cover
        return 'APIError(code=%s): %s | %s' % (self.code, self.message, self.result)


class RequestException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'RequestException: %s' % self.message


class BaseClient(ABC):
    API_URL = 'https://api.wallex.ir'
    PUBLIC_API_VERSION = 'v1'

    REQUEST_TIMEOUT: float = 10

    @abstractmethod
    def __init__(
            self, requests_params: t.Optional[t.Dict[str, str]] = None,
    ):
        self._requests_params = requests_params
        self.session = self._init_session()

    @staticmethod
    def _get_kwargs(locals_: t.Dict, del_keys: t.List[str] = None, del_nones: bool = False) -> t.Dict:
        _del_keys = ['self', 'cls']
        if del_keys is not None:
            _del_keys.extend(del_keys)

        if del_nones is True:
            return {key: value for key, value in locals_.items() if (key not in _del_keys) and (value is not None)}

        return {key: value for key, value in locals_.items() if key not in _del_keys}

    @staticmethod
    def _get_headers() -> t.Dict:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        return headers

    def _create_api_uri(self, path: str, version: str = PUBLIC_API_VERSION) -> str:
        if version is None or version.isspace() or version == '':
            return self.API_URL + '/' + path
        return self.API_URL + '/' + version + '/' + path

    def _get_request_kwargs(self, method, signed: bool, **kwargs) -> t.Dict:
        kwargs['timeout'] = self.REQUEST_TIMEOUT

        if self._requests_params:
            kwargs.update(self._requests_params)

        data = kwargs.get('data', None)
        if data and isinstance(data, dict):
            kwargs['data'] = data

            if 'requests_params' in kwargs['data']:
                kwargs.update(kwargs['data']['requests_params'])
                del (kwargs['data']['requests_params'])

        if signed is True:
            headers = kwargs.get('headers', {})
            kwargs['headers'] = headers

        if data and method == 'get':
            kwargs['params'] = '&'.join('%s=%s' % (data[0], data[1]) for data in kwargs['data'])
            del (kwargs['data'])

        return kwargs

    @abstractmethod
    def _init_session(self) -> t.Union[requests.Session, aiohttp.ClientSession]:
        raise NotImplementedError('_init_session not implemented')

    @abstractmethod
    def _request(self, method: str, uri: str, signed: bool, **kwargs):
        raise NotImplementedError('_request not implemented')

    @staticmethod
    @abstractmethod
    def _handle_response(response: t.Union[requests.Response, aiohttp.ClientResponse]):
        raise NotImplementedError('_handle_response not implemented')

    @abstractmethod
    def _request_api(
            self, method: str, path: str, signed: bool = False, version=PUBLIC_API_VERSION, **kwargs
    ):
        raise NotImplementedError('_request_api not implemented')

    @abstractmethod
    def _get(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs) -> t.Dict:
        raise NotImplementedError('_get not implemented')

    @abstractmethod
    def _post(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs) -> t.Dict:
        raise NotImplementedError('_post not implemented')

    @abstractmethod
    def _put(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs) -> t.Dict:
        raise NotImplementedError('_put not implemented')

    @abstractmethod
    def _delete(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs) -> t.Dict:
        raise NotImplementedError('_delete not implemented')

    @abstractmethod
    def close_connection(self):
        raise NotImplementedError('close_connection not implemented')


class SyncClient(BaseClient):
    def __init__(self):
        super().__init__()

    def _init_session(self) -> requests.Session:
        return requests.Session()

    @staticmethod
    def _handle_response(response: requests.Response):
        if not (200 <= response.status_code < 300):
            raise APIException(response, response.status_code, response.text)
        try:
            return response.json()
        except ValueError:
            raise RequestException('Invalid Response: %s' % response.text)

    def _request(self, method: str, uri: str, signed: bool, **kwargs) -> t.Dict:
        kwargs = self._get_request_kwargs(method, signed, **kwargs)

        self.response = getattr(self.session, method)(uri, **kwargs)
        return self._handle_response(self.response)

    def _request_api(
            self, method: str, path: str, signed: bool = False, version=BaseClient.PUBLIC_API_VERSION, **kwargs
    ) -> t.Dict:
        uri = self._create_api_uri(path, version)
        return self._request(method, uri, signed, **kwargs)

    def _get(self, path, signed=False, version=BaseClient.PUBLIC_API_VERSION, **kwargs) -> t.Dict:
        return self._request_api('get', path, signed, version, **kwargs)

    def _post(self, path, signed=False, version=BaseClient.PUBLIC_API_VERSION, **kwargs) -> t.Dict:
        return self._request_api('post', path, signed, version, **kwargs)

    def _put(self, path, signed=False, version=BaseClient.PUBLIC_API_VERSION, **kwargs) -> t.Dict:
        return self._request_api('put', path, signed, version, **kwargs)

    def _delete(self, path, signed=False, version=BaseClient.PUBLIC_API_VERSION, **kwargs) -> t.Dict:
        return self._request_api('delete', path, signed, version, **kwargs)

    def close_connection(self):
        self.session.close()


class AsyncClient(BaseClient):
    def __init__(self, loop: t.Optional[asyncio.AbstractEventLoop] = None):
        self.loop = loop or asyncio.get_event_loop()
        super().__init__()

    # @classmethod
    # async def create(cls, loop: t.Optional[asyncio.AbstractEventLoop] = None):
    #     return cls(loop)

    def __aenter__(self):
        return self

    def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()
        return False

    def _init_session(self) -> aiohttp.ClientSession:
        session = aiohttp.ClientSession(
            loop=self.loop,
            headers=self._get_headers()
        )
        return session

    @staticmethod
    async def _handle_response(response: aiohttp.ClientResponse) -> t.Dict:
        if not str(response.status).startswith('2'):
            raise APIException(response, response.status, await response.text())
        try:
            return await response.json()
        except ValueError:
            txt = await response.text()
            raise RequestException(f'Invalid Response: {txt}')

    async def _request(self, method, uri: str, signed: bool, **kwargs) -> t.Dict:
        kwargs = self._get_request_kwargs(method, signed, **kwargs)

        async with getattr(self.session, method)(uri, **kwargs) as response:
            self.response = response
            return await self._handle_response(response)

    async def _request_api(self, method, path, signed=False, version=BaseClient.PUBLIC_API_VERSION, **kwargs) -> t.Dict:
        uri = self._create_api_uri(path, version)
        return await self._request(method, uri, signed, **kwargs)

    async def _get(self, path, signed=False, version=BaseClient.PUBLIC_API_VERSION, **kwargs) -> t.Dict:
        return await self._request_api('get', path, signed, version, **kwargs)

    async def _post(self, path, signed=False, version=BaseClient.PUBLIC_API_VERSION, **kwargs) -> t.Dict:
        return await self._request_api('post', path, signed, version, **kwargs)

    async def _put(self, path, signed=False, version=BaseClient.PUBLIC_API_VERSION, **kwargs) -> t.Dict:
        return await self._request_api('put', path, signed, version, **kwargs)

    async def _delete(self, path, signed=False, version=BaseClient.PUBLIC_API_VERSION, **kwargs) -> t.Dict:
        return await self._request_api('delete', path, signed, version, **kwargs)

    async def close_connection(self):
        await self.session.close()

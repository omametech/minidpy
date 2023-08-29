import aiohttp
import asyncio


_BASE_URL = "https://discord.com/api"


class REST:
    def __init__(
        self, session: aiohttp.ClientSession, token: str, *, is_bot=True, version=10
    ):
        self._session = session
        self._token = token
        self._is_bot = is_bot
        self._version = version

        self._session.headers["Authorization"] = (
            "Bot " if is_bot else ""
        ) + self._token

    async def _request(self, method: str, endpoint: str, data: any):
        resp = await self._session.request(
            method, f"{_BASE_URL}/v{self._version}{endpoint}", json=data
        )
        data = await resp.json()
        if "retry_after" in data:
            await asyncio.sleep(data["retry_after"])
            return self._request(method, endpoint, data)
        if "code" in data and "message" in data:
            raise RESTError(data["code"], data["message"])
        return data

    async def get(self, endpoint: str):
        return self._request("GET", endpoint, None)

    async def post(self, endpoint: str, data: any):
        return self._request("POST", endpoint, data)


class RESTError(Exception):
    def __init__(self, code: int, message: str):
        super(f"Error {code}: {message}")
        self.code = code
        self.message = message

from logging import getLogger
from socket import AF_INET
from typing import Optional

import aiohttp
from aiohttp import ClientResponse, ClientSession

from application.core.exceptions.external_service import (
    ExternalServiceClientException,
    ExternalServiceServerException,
)

logger = getLogger(__name__)


SIZE_POOL_AIOHTTP = 100
CLIENT_TIME_OUT = 2


def json_encoder_extend(obj):
    return str(obj)


class Aiohttp:
    aiohttp_client: Optional[aiohttp.ClientSession] = None

    @classmethod
    def get_aiohttp_client(
        cls,
        client_timeout: int = CLIENT_TIME_OUT,
        limit_per_host=SIZE_POOL_AIOHTTP,
    ) -> aiohttp.ClientSession:
        if cls.aiohttp_client is None:
            timeout = aiohttp.ClientTimeout(total=client_timeout)
            connector = aiohttp.TCPConnector(
                family=AF_INET, limit_per_host=limit_per_host
            )
            cls.aiohttp_client = aiohttp.ClientSession(
                timeout=timeout, connector=connector
            )
        return cls.aiohttp_client

    @classmethod
    async def close_aiohttp_client(cls) -> None:
        if cls.aiohttp_client:
            await cls.aiohttp_client.close()
            cls.aiohttp_client = None

    @staticmethod
    async def on_startup() -> None:
        Aiohttp.get_aiohttp_client()

    @staticmethod
    async def on_shutdown() -> None:
        await Aiohttp.close_aiohttp_client()


class BaseHttpClient:
    session: ClientSession

    async def _post(
        self,
        url: str,
        data: dict | None = None,
        dict_data: dict | None = None,
        q_params: dict | None = None,
        headers: dict | None = None,
        ssl: bool = True,
    ) -> ClientResponse:
        resp = await self.session.post(
            url,
            data=data,
            json=dict_data,
            params=q_params,
            headers=headers,
            ssl=ssl,
        )
        if resp.status == 200:
            return resp
        elif 400 <= resp.status < 500:
            text = await resp.text()
            logger.error(f"ExternalServiceClientException: {text}")
            raise ExternalServiceClientException(f"{text}")
        elif resp.status >= 500:
            text = await resp.text()
            logger.error(f"ExternalServiceServerException: {text}")
            raise ExternalServiceServerException(f"{text}")
        return resp

    async def _get(
        self,
        url: str,
        q_params: dict | None = None,
        headers: dict | None = None,
        ssl: bool = True,
    ) -> ClientResponse:
        resp = await self.session.post(url, params=q_params, headers=headers, ssl=ssl)
        if resp.status == 200:
            return resp
        elif 400 <= resp.status < 500:
            text = await resp.text()
            logger.error(f"ExternalServiceClientException: {text}")
            raise ExternalServiceClientException(f"{text}")
        elif resp.status >= 500:
            text = await resp.text()
            logger.error(f"ExternalServiceServerException: {text}")
            raise ExternalServiceServerException(f"{text}")
        return resp

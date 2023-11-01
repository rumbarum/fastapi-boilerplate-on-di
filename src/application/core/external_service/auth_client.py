import base64
import logging
from typing import Literal

from aiohttp import ClientSession

from application.core.enums import ResponseCode
from application.core.exceptions.token import TokenDecodeException, TokenExpireException
from application.core.external_service.http_client import BaseHttpClient

logger = logging.getLogger(__name__)


def encode_base64(string) -> str:
    encoded_bytes = base64.b64encode(string.encode("utf-8"))
    encoded_string = encoded_bytes.decode("utf-8")
    return encoded_string


class AuthClient(BaseHttpClient):

    json_content_type = {"Content-Type": "application/json"}
    form_url_content_type = {"Content-Type": "application/x-www-form-urlencoded"}

    def __init__(
        self,
        auth_base_url: str,
        client_id: str,
        client_secret: str,
        refresh_token_key: str,
        session: ClientSession,
        ssl: bool = True,
        scope: list[str] | None = None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token_key = refresh_token_key
        self.session = session
        self.ssl = ssl
        self._token_issue_url = auth_base_url + "/oauth2/token"
        self._token_verify_url = auth_base_url + "/oauth2/verify"
        self._token_refresh_url = auth_base_url + "/oauth2/token"
        self._token_revoke_url = auth_base_url + "/oauth2/revoke"
        if scope is not None:
            self.scope = ",".join(scope)
        else:
            self.scope = ""

    def get_basic_header(self) -> dict:
        return {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic "
            + encode_base64(self._client_id + ":" + self._client_secret),
        }

    async def get_server_access_token(self) -> str:
        q_params = {"grant_type": "client_credentials", "scope": self.scope}
        resp = await self._post(
            self._token_issue_url,
            q_params=q_params,
            headers={**self.get_basic_header(), **self.form_url_content_type},
        )
        resp_json = await resp.json()
        return resp_json.get("access_token", None)

    async def get_bearer_header(self) -> dict:
        atk = await self.get_server_access_token()
        return {
            "Authorization": "Bearer " + atk,
            "Content-Type": "application/json",
        }

    def get_header_cookie(self, key: str, value: str) -> dict:
        return {"Cookie": f"{key}={value}"}

    async def is_token_valid(
        self,
        token: str,
        token_type: Literal["access_token", "refresh_token"] = "access_token",
    ) -> bool:
        resp = await self._post(
            url=self._token_verify_url,
            dict_data={"token": token, "tokenType": token_type},
            headers={**self.get_basic_header(), **self.json_content_type},
        )
        resp_json = await resp.json()
        resp_code = resp_json.get("code")
        if resp_code == ResponseCode.OK:
            return True
        if resp_code == ResponseCode.TOKEN_INVALID:
            raise TokenDecodeException()
        if resp_code == ResponseCode.TOKEN_EXPIRED:
            raise TokenExpireException()
        return False

    async def refresh_token(self, refresh_token: str) -> dict:
        payload = {
            "grant_type": "refresh_token",
            "refresh_token_key": self._refresh_token_key,
        }
        cookie = self.get_header_cookie(self._refresh_token_key, refresh_token)
        resp = await self._post(
            self._token_refresh_url,
            data=payload,
            headers={
                **self.get_basic_header(),
                **cookie,
                **self.form_url_content_type,
            },
        )
        resp_json = await resp.json()
        return resp_json

    async def revoke_token(
        self, token: str, token_type: Literal["access_token", "refresh_token"]
    ) -> None:
        payload = {"token": token, "token_type_hint": token_type}
        resp = await self._post(
            self._token_revoke_url,
            data=payload,
            headers={**self.get_basic_header(), **self.form_url_content_type},
        )

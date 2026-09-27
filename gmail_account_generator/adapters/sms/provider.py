"""SMS provider abstraction. smspool + sms-activate adapters behind one iface."""
from __future__ import annotations

import asyncio

import httpx
import structlog

log = structlog.get_logger(__name__)

_ENDPOINTS = {
    "smspool": "https://api.smspool.net/purchase/sms",
    "sms-activate": "https://api.sms-activate.org/stubs/handler_api.php",
}


class SmsProvider:
    def __init__(self, provider: str, api_key: str) -> None:
        if provider not in _ENDPOINTS:
            raise ValueError(f"unknown sms provider: {provider}")
        self._provider = provider
        self._api_key = api_key
        self._endpoint = _ENDPOINTS[provider]
        self._client = httpx.AsyncClient(timeout=30.0)

    async def request_number(self, service: str, proxy: str | None = None) -> str:
        params = {"key": self._api_key, "service": service, "country": "0"}
        r = await self._client.get(self._endpoint, params=params, proxy=proxy)
        r.raise_for_status()
        # smspool returns {"number": "..."}; sms-activate returns "ACCESS_NUMBER:id:num"
        body = r.text
        if body.startswith("ACCESS_NUMBER"):
            return body.split(":", 2)[2]
        return r.json().get("number", "")

    async def wait_for_code(self, phone: str, timeout: int = 120) -> str | None:
        deadline = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < deadline:
            await asyncio.sleep(5)
            r = await self._client.get(
                self._endpoint,
                params={"key": self._api_key, "action": "getStatus", "id": phone},
            )
            text = r.text
            if text.startswith("STATUS_OK"):
                return text.split(":", 1)[1]
        log.warning("sms.timeout", phone=phone[-4:])
        return None
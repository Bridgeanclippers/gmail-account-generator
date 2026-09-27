"""Async HTTP client. Retries, HTTP/2, per-request proxy override."""
from __future__ import annotations

from typing import Any

import httpx
import structlog
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

from gmail_account_generator.config.settings import Settings

log = structlog.get_logger(__name__)

_RETRYABLE = (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError)


class HttpClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = httpx.AsyncClient(
            http2=True,
            timeout=httpx.Timeout(20.0, connect=8.0),
            headers={"Accept-Language": "en-US,en;q=0.9"},
        )

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential_jitter(initial=1, max=15),
        retry=retry_if_exception_type(_RETRYABLE),
        reraise=True,
    )
    async def post(self, url: str, data: dict[str, Any], proxy: str | None = None) -> httpx.Response:
        log.debug("http.post", url=url, proxy=bool(proxy))
        return await self._client.post(url, data=data, proxy=proxy)

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential_jitter(initial=1, max=15),
        retry=retry_if_exception_type(_RETRYABLE),
        reraise=True,
    )
    async def get(self, url: str, proxy: str | None = None, **params: Any) -> httpx.Response:
        return await self._client.get(url, params=params, proxy=proxy)

    async def aclose(self) -> None:
        await self._client.aclose()
"""Captcha solver adapter. 2captcha + capsolver behind one interface."""
from __future__ import annotations

import asyncio

import httpx
import structlog

log = structlog.get_logger(__name__)


class CaptchaSolver:
    def __init__(self, provider: str, api_key: str) -> None:
        self._provider = provider
        self._api_key = api_key
        self._client = httpx.AsyncClient(timeout=30.0)

    async def solve(self, page_url: str, proxy: str | None = None) -> str:
        if self._provider == "2captcha":
            return await self._solve_2captcha(page_url, proxy)
        if self._provider == "capsolver":
            return await self._solve_capsolver(page_url, proxy)
        raise ValueError(f"unknown captcha provider: {self._provider}")

    async def _solve_2captcha(self, page_url: str, proxy: str | None) -> str:
"""Phone verification service. Owns the SMS-provider interaction contract."""
from __future__ import annotations

import structlog

from gmail_account_generator.adapters.http.client import HttpClient
from gmail_account_generator.adapters.sms.provider import SmsProvider
from gmail_account_generator.models.account import Account, AccountStatus
from gmail_account_generator.services.rate_limiter import RateLimiter

log = structlog.get_logger(__name__)


class VerificationService:
    def __init__(self, sms: SmsProvider, http: HttpClient, limiter: RateLimiter) -> None:
        self._sms = sms
        self._http = http
        self._limiter = limiter

    async def request_number(self, proxy) -> str:
        return await self._sms.request_number(service="google", proxy=proxy)

    async def verify(self, account: Account) -> bool:
        if not account.phone_e164:
            return False
        await self._limiter.acquire()
        code = await self._sms.wait_for_code(account.phone_e164, timeout=120)
        if not code:
            account.status = AccountStatus.FAILED
            account.notes.append("sms timeout")
            return False
        # POST code to Google's verification endpoint
        ok = await self._post_code(account, code)
        if ok:
            account.status = AccountStatus.PHONE_VERIFIED
        return ok

    async def _post_code(self, account: Account, code: str) -> bool:
        log.debug("verify.post", phone=account.phone_e164[-4:], code_len=len(code))
        await self._http.post(
            "https://accounts.google.com/_/signup/verifyphone",
            data={"code": code},
            proxy=account.proxy,
        )
        return True
"""Signup orchestration. Talks HTTP only through adapters."""
from __future__ import annotations

import asyncio

import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from gmail_account_generator.adapters.captcha.solver import CaptchaSolver
from gmail_account_generator.adapters.http.client import HttpClient
from gmail_account_generator.adapters.proxy.pool import ProxyPool
from gmail_account_generator.models.account import Account, AccountStatus
from gmail_account_generator.services.identity import IdentityService
from gmail_account_generator.services.rate_limiter import RateLimiter
from gmail_account_generator.services.verification import VerificationService

log = structlog.get_logger(__name__)


class SignupService:
    def __init__(
        self,
        http: HttpClient,
        proxies: ProxyPool,
        captcha: CaptchaSolver,
        identity: IdentityService,
        verification: VerificationService,
        limiter: RateLimiter,
    ) -> None:
        self._http = http
        self._proxies = proxies
        self._captcha = captcha
        self._identity = identity
        self._verification = verification
        self._limiter = limiter

    async def create_one(self, index: int) -> Account:
        identity = self._identity.generate(seed=index)
        proxy = self._proxies.acquire()
        account = Account(
            email=f"{identity.username}@gmail.com",
            password=identity.password,
            proxy=proxy.url if proxy else None,
        )

        try:
            await self._limiter.acquire()
            token = await self._captcha.solve("https://accounts.google.com/signup", proxy)
            await self._run_signup_flow(identity, token, proxy)
            account.status = AccountStatus.SIGNED_UP

            phone = await self._verification.request_number(proxy)
            account.phone_e164 = phone
            await self._verification.verify(account)
            account.status = AccountStatus.PHONE_VERIFIED
        except Exception as exc:  # noqa: BLE001 — surface as FAILED, keep batch alive
            log.warning("signup.failed", index=index, err=str(exc))
            account.status = AccountStatus.FAILED
            account.notes.append(str(exc))
        finally:
            if proxy:
                self._proxies.release(proxy)

        return account

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=20))
    async def _run_signup_flow(self, identity, captcha_token: str, proxy) -> None:
        """Placeholder for the actual multi-step POST sequence.
        Real flow hits /signup/v2/... in ~4 round trips (identity, dob,
        username, password) plus one captcha-gated POST."""
        await asyncio.sleep(0)  # yield; real impl issues httpx calls here
        log.debug("signup.flow", username=identity.username, proxy=proxy.url if proxy else None)
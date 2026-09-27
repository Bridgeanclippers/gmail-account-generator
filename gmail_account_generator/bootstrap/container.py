"""Dependency wiring. Thin: constructs adapters + services, hands them to handlers."""
from __future__ import annotations

from dataclasses import dataclass

from gmail_account_generator.adapters.http.client import HttpClient
from gmail_account_generator.adapters.proxy.pool import ProxyPool
from gmail_account_generator.adapters.sms.provider import SmsProvider
from gmail_account_generator.adapters.captcha.solver import CaptchaSolver
from gmail_account_generator.adapters.windows.fingerprint import FingerprintAdapter
from gmail_account_generator.config.settings import Settings
from gmail_account_generator.services.identity import IdentityService
from gmail_account_generator.services.signup import SignupService
from gmail_account_generator.services.verification import VerificationService
from gmail_account_generator.services.profile_store import ProfileStore
from gmail_account_generator.services.rate_limiter import RateLimiter


@dataclass(slots=True)
class Container:
    settings: Settings
    http: HttpClient
    proxies: ProxyPool
    sms: SmsProvider
    captcha: CaptchaSolver
    fingerprint: FingerprintAdapter
    identity: IdentityService
    signup: SignupService
    verification: VerificationService
    store: ProfileStore
    limiter: RateLimiter


def build_container(settings: Settings) -> Container:
    http = HttpClient(settings)
    proxies = ProxyPool.from_file(settings.proxy_file)
    sms = SmsProvider(settings.sms_provider, settings.sms_api_key)
    captcha = CaptchaSolver(settings.captcha_provider, settings.captcha_api_key)
    fingerprint = FingerprintAdapter(settings.fingerprint_profile)

    identity = IdentityService(settings, fingerprint)
    store = ProfileStore(settings.profile_dir)
    limiter = RateLimiter(settings.rate_limit_per_min)
    verification = VerificationService(sms, http, limiter)
    signup = SignupService(http, proxies, captcha, identity, verification, limiter)

    return Container(
        settings=settings,
        http=http,
        proxies=proxies,
        sms=sms,
        captcha=captcha,
        fingerprint=fingerprint,
        identity=identity,
        signup=signup,
        verification=verification,
        store=store,
        limiter=limiter,
    )
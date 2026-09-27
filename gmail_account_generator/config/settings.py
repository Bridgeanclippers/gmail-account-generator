"""Runtime settings. YAML + env override. Never commit local.yaml."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv


@dataclass(slots=True)
class Settings:
    profile_dir: Path = Path("generated/profiles")
    proxy_file: Path = Path("config/proxies.txt")
    sms_provider: str = "smspool"
    captcha_provider: str = "2captcha"
    fingerprint_profile: str = "chrome_win_2026"
    rate_limit_per_min: int = 6
    headless: bool = True
    log_level: str = "INFO"
    user_agent_pool: list[str] = field(default_factory=list)

    sms_api_key: str = ""
    captcha_api_key: str = ""

    @classmethod
    def load(cls, path: str | Path) -> "Settings":
        load_dotenv()
        raw: dict = {}
        p = Path(path)
        if p.exists():
            raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}

        s = cls(
            profile_dir=Path(raw.get("profile_dir", cls.profile_dir)),
            proxy_file=Path(raw.get("proxy_file", cls.proxy_file)),
            sms_provider=raw.get("sms_provider", cls.sms_provider),
            captcha_provider=raw.get("captcha_provider", cls.captcha_provider),
            fingerprint_profile=raw.get("fingerprint_profile", cls.fingerprint_profile),
            rate_limit_per_min=int(raw.get("rate_limit_per_min", cls.rate_limit_per_min)),
            headless=bool(raw.get("headless", cls.headless)),
            log_level=raw.get("log_level", cls.log_level),
            user_agent_pool=list(raw.get("user_agent_pool", [])),
        )
        s.sms_api_key = os.getenv("SMS_API_KEY", "")
        s.captcha_api_key = os.getenv("CAPTCHA_API_KEY", "")
        return s
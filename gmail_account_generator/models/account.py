from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class AccountStatus(str, Enum):
    PENDING = "pending"
    SIGNED_UP = "signed_up"
    PHONE_VERIFIED = "phone_verified"
    FAILED = "failed"
    BANNED = "banned"


@dataclass(slots=True)
class Account:
    email: str
    password: str
    status: AccountStatus = AccountStatus.PENDING
    recovery_email: str | None = None
    phone_e164: str | None = None
    proxy: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    notes: list[str] = field(default_factory=list)

    def to_export(self) -> dict:
        return {
            "email": self.email,
            "password": self.password,
            "status": self.status.value,
            "recovery_email": self.recovery_email,
            "phone_e164": self.phone_e164,
            "proxy": self.proxy,
            "created_at": self.created_at.isoformat(),
        }
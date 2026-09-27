from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Identity:
    first_name: str
    last_name: str
    birth_day: int
    birth_month: int
    birth_year: int
    gender: str
    username: str
    password: str
    recovery_email: str | None = None
    locale: str = "en-US"
    timezone: str = "America/New_York"
    extra: dict[str, str] = field(default_factory=dict)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
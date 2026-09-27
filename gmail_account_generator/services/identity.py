"""Generate plausible identities. Deterministic per seed for reproducibility."""
from __future__ import annotations

import secrets
import string

from faker import Faker

from gmail_account_generator.adapters.windows.fingerprint import FingerprintAdapter
from gmail_account_generator.config.settings import Settings
from gmail_account_generator.models.identity import Identity

_ALPHABET = string.ascii_lowercase + string.digits


class IdentityService:
    def __init__(self, settings: Settings, fingerprint: FingerprintAdapter) -> None:
        self._settings = settings
        self._fp = fingerprint
        self._faker = Faker(locale="en_US")

    def generate(self, seed: int | None = None) -> Identity:
        if seed is not None:
            Faker.seed(seed)

        first = self._faker.first_name()
        last = self._faker.last_name()
        year = self._faker.random_int(min=1975, max=2004)
        month = self._faker.random_int(min=1, max=12)
        day = self._faker.random_int(min=1, max=28)

        username = self._username(first, last)
        password = self._password()
        fp = self._fp.current()

        return Identity(
            first_name=first,
            last_name=last,
            birth_day=day,
            birth_month=month,
            birth_year=year,
            gender=self._faker.random_element(("male", "female")),
            username=username,
            password=password,
            locale=fp.languages[0],
            timezone=fp.timezone,
        )

    def _username(self, first: str, last: str) -> str:
        base = f"{first.lower()}.{last.lower()}"
        suffix = "".join(secrets.choice(_ALPHABET) for _ in range(4))
        return f"{base}{suffix}"

    def _password(self) -> str:
        core = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        return f"{core}!{secrets.choice(string.ascii_uppercase)}"
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .account import Account


@dataclass(slots=True)
class Batch:
    batch_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    accounts: list[Account] = field(default_factory=list)
    concurrency: int = 4
    label: str = ""

    @property
    def succeeded(self) -> list[Account]:
        from .account import AccountStatus
        return [a for a in self.accounts if a.status == AccountStatus.PHONE_VERIFIED]

    @property
    def failed(self) -> list[Account]:
        from .account import AccountStatus
        return [a for a in self.accounts if a.status == AccountStatus.FAILED]
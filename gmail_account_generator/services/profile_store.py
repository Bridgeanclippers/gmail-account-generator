"""On-disk profile store. One JSON per batch, plus a rolling index."""
from __future__ import annotations

import json
from pathlib import Path

from gmail_account_generator.models.account import Account, AccountStatus
from gmail_account_generator.models.batch import Batch


class ProfileStore:
    def __init__(self, root: Path) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)
        self._index = self._root / "index.json"
        if not self._index.exists():
            self._index.write_text("[]", encoding="utf-8")

    def save_batch(self, batch: Batch) -> Path:
        path = self._root / f"{batch.batch_id}.json"
        payload = {
            "batch_id": batch.batch_id,
            "created_at": batch.created_at.isoformat(),
            "concurrency": batch.concurrency,
            "label": batch.label,
            "accounts": [a.to_export() for a in batch.accounts],
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self._append_index(batch.batch_id)
        return path

    def load_batch(self, batch_id: str) -> Batch:
        path = self._root / f"{batch_id}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        batch = Batch(batch_id=payload["batch_id"], label=payload.get("label", ""))
        for row in payload["accounts"]:
            batch.accounts.append(
                Account(
                    email=row["email"],
                    password=row["password"],
                    status=AccountStatus(row["status"]),
                    recovery_email=row.get("recovery_email"),
                    phone_e164=row.get("phone_e164"),
                    proxy=row.get("proxy"),
                )
            )
        return batch

    def _append_index(self, batch_id: str) -> None:
        ids: list[str] = json.loads(self._index.read_text(encoding="utf-8"))
        if batch_id not in ids:
            ids.append(batch_id)
        self._index.write_text(json.dumps(ids, indent=2), encoding="utf-8")
"""Thin handler: dump a batch to json/csv/txt."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from gmail_account_generator.bootstrap.container import Container


def handle(container: Container, batch_id: str, fmt: str) -> Path:
    batch = container.store.load_batch(batch_id)
    out_dir = container.settings.profile_dir / "exports"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{batch_id}.{fmt}"

    rows = [a.to_export() for a in batch.accounts]
    if fmt == "json":
        path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    elif fmt == "csv":
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=rows[0].keys() if rows else [])
            w.writeheader()
            w.writerows(rows)
    else:
        path.write_text("\n".join(f"{r['email']}:{r['password']}" for r in rows), encoding="utf-8")
    return path
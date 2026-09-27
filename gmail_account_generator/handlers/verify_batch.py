"""Thin handler: re-verify every account in a stored batch."""
from __future__ import annotations

import asyncio

from gmail_account_generator.bootstrap.container import Container


async def handle(container: Container, batch_id: str) -> None:
    batch = container.store.load_batch(batch_id)
    await asyncio.gather(*(container.verification.verify(acc) for acc in batch.accounts))
    container.store.save_batch(batch)
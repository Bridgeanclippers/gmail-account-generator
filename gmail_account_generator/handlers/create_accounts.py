"""Thin handler: run N signups through SignupService, persist to ProfileStore."""
from __future__ import annotations

import asyncio

import structlog
from rich.console import Console

from gmail_account_generator.bootstrap.container import Container
from gmail_account_generator.models.batch import Batch

log = structlog.get_logger(__name__)
console = Console()


async def handle(container: Container, count: int, concurrency: int) -> Batch:
    batch = Batch(concurrency=concurrency)
    sem = asyncio.Semaphore(concurrency)

    async def one(i: int):
        async with sem:
            acct = await container.signup.create_one(index=i)
            batch.accounts.append(acct)
            console.print(f"[cyan]{i:03d}[/] {acct.email} -> {acct.status.value}")

    await asyncio.gather(*(one(i) for i in range(count)))
    container.store.save_batch(batch)
    log.info("batch.complete", batch_id=batch.batch_id, ok=len(batch.succeeded), fail=len(batch.failed))
    return batch
"""Entry point. Wires settings, builds container, dispatches to handlers."""
from __future__ import annotations

import asyncio
import sys

import click
from rich.console import Console

from gmail_account_generator.bootstrap.container import build_container
from gmail_account_generator.config.settings import Settings
from gmail_account_generator.handlers import create_accounts, verify_batch, export_profiles

console = Console()


@click.group()
@click.option("--config", "config_path", default="config/local.yaml", show_default=True)
@click.pass_context
def main(ctx: click.Context, config_path: str) -> None:
    """gmail-account-generator — research CLI."""
    settings = Settings.load(config_path)
    ctx.obj = build_container(settings)


@main.command("run")
@click.option("-n", "--count", default=1, type=int)
@click.option("--concurrency", default=4, type=int)
@click.pass_obj
def run_cmd(container, count: int, concurrency: int) -> None:
    """Create N accounts through the signup handler."""
    asyncio.run(create_accounts.handle(container, count=count, concurrency=concurrency))


@main.command("verify")
@click.argument("batch_id")
@click.pass_obj
def verify_cmd(container, batch_id: str) -> None:
    """Re-run verification for a stored batch."""
    asyncio.run(verify_batch.handle(container, batch_id))


@main.command("export")
@click.argument("batch_id")
@click.option("--fmt", type=click.Choice(["json", "csv", "txt"]), default="json")
@click.pass_obj
def export_cmd(container, batch_id: str, fmt: str) -> None:
    """Export a batch to the given format."""
    export_profiles.handle(container, batch_id, fmt)


if __name__ == "__main__":
    sys.exit(main())
"""Manual signal entry via CLI."""

import click
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from signal_collectors.base import Signal
from strategic_memory.store import SignalStore


@click.command()
@click.option("--text", "-t", required=True, help="Signal text content")
@click.option("--source", "-s", default="manual", help="Signal source")
@click.option("--category", "-c", default="manual_observation", help="Signal category")
@click.option("--url", "-u", default=None, help="Optional URL")
@click.option("--tags", multiple=True, help="Tags to attach")
def submit(text: str, source: str, category: str, url: str | None, tags: tuple):
    """Manually submit a signal to the system."""
    signal = Signal(
        text=text,
        source=source,
        category=category,
        url=url,
        collected_at=datetime.utcnow(),
        tags=list(tags),
    )

    # Store immediately in memory
    store = SignalStore()
    store.add_signal(signal)

    click.echo(f"✓ Signal stored: {signal.id}")
    click.echo(f"  Category: {signal.category}")
    click.echo(f"  Source: {signal.source}")


if __name__ == "__main__":
    submit()
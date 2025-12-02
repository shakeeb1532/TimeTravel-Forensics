import click
click.echo = lambda *args, **kwargs: None

import sys
import click
from . import recorder, trigger
from .utils import info, success


@click.group()
def main():
    """TTFR - Time Travel Forensics Recorder CLI"""
    pass


# -------------------------
# Commands
# -------------------------

@main.command()
def start():
    """Start telemetry recording."""
    recorder.start()
    success("TTFR running.")


@main.command()
def stop():
    """Stop telemetry recording."""
    recorder.stop()
    success("TTFR stopped.")


@main.command()
def status():
    """Show recorder status."""
    if recorder.status():
        info("Status: RUNNING")
    else:
        info("Status: STOPPED")


@main.command()
@click.option("--reason", default="manual", help="Flush trigger reason")
def flush(reason):
    """Flush the ring buffer and save snapshot."""
    trigger.flush(reason)


@main.command()
@click.argument("path")
def replay(path):
    """Replay a TTFR snapshot"""
    from .replay import replay as _replay
    _replay(path)


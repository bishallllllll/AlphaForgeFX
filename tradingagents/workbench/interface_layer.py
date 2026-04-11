"""Workbench Part 7: CLI/interface access helpers."""

from __future__ import annotations

import typer

from cli.main import app as cli_app


def get_cli_app() -> typer.Typer:
    """Return the Typer CLI application for embedding/testing."""
    return cli_app

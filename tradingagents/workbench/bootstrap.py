"""Workbench Part 1: bootstrap and runtime configuration helpers.

This module is intentionally lightweight so you can import it quickly in
Jupyter notebooks before initializing heavier graph/LLM components.
"""

from __future__ import annotations

from typing import Any, Dict

from dotenv import load_dotenv

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.config import get_config, set_config


def load_environment() -> None:
    """Load environment variables from .env into process environment."""
    load_dotenv()


def get_default_config_copy() -> Dict[str, Any]:
    """Return a mutable copy of the package default config."""
    return DEFAULT_CONFIG.copy()


def apply_runtime_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply runtime config to dataflow router and return active config snapshot."""
    set_config(config)
    return get_config()

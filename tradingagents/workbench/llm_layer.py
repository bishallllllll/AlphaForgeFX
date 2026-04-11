"""Workbench Part 2: LLM client factory helpers."""

from __future__ import annotations

from typing import Any, Optional

from tradingagents.llm_clients import create_llm_client


def create_client(provider: str, model: str, base_url: Optional[str] = None, **kwargs: Any):
    """Create a provider client without constructing the full trading graph."""
    return create_llm_client(provider=provider, model=model, base_url=base_url, **kwargs)


def create_llm(provider: str, model: str, base_url: Optional[str] = None, **kwargs: Any):
    """Create and return a configured LangChain-compatible LLM object."""
    client = create_client(provider=provider, model=model, base_url=base_url, **kwargs)
    return client.get_llm()

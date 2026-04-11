"""Workbench Part 5: agent factory introspection helpers."""

from __future__ import annotations

from typing import Dict, Callable

from tradingagents import agents as _agents_pkg


AGENT_FACTORIES: Dict[str, Callable] = {
    "create_market_analyst": _agents_pkg.create_market_analyst,
    "create_social_media_analyst": _agents_pkg.create_social_media_analyst,
    "create_news_analyst": _agents_pkg.create_news_analyst,
    "create_fundamentals_analyst": _agents_pkg.create_fundamentals_analyst,
    "create_macro_analyst": _agents_pkg.create_macro_analyst,
    "create_bull_researcher": _agents_pkg.create_bull_researcher,
    "create_bear_researcher": _agents_pkg.create_bear_researcher,
    "create_research_manager": _agents_pkg.create_research_manager,
    "create_trader": _agents_pkg.create_trader,
    "create_forex_trader": _agents_pkg.create_forex_trader,
    "create_aggressive_debator": _agents_pkg.create_aggressive_debator,
    "create_neutral_debator": _agents_pkg.create_neutral_debator,
    "create_conservative_debator": _agents_pkg.create_conservative_debator,
    "create_risk_manager": _agents_pkg.create_risk_manager,
    "create_executor": _agents_pkg.create_executor,
}


def list_factories() -> list[str]:
    """List available agent factory function names."""
    return sorted(AGENT_FACTORIES.keys())


def get_factory(name: str) -> Callable:
    """Get one factory by name."""
    if name not in AGENT_FACTORIES:
        raise KeyError(f"Unknown factory: {name}")
    return AGENT_FACTORIES[name]

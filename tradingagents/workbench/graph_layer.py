"""Workbench Part 6: graph construction and one-shot execution helpers."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph


def create_graph(config: Optional[Dict[str, Any]] = None, debug: bool = False, selected_analysts: Optional[list[str]] = None) -> TradingAgentsGraph:
    """Create a TradingAgentsGraph with optional overrides."""
    active_config = (config or DEFAULT_CONFIG).copy()
    analysts = selected_analysts or ["market", "social", "news", "fundamentals"]
    return TradingAgentsGraph(debug=debug, config=active_config, selected_analysts=analysts)


def run_once(instrument: str, trade_date: str, config: Optional[Dict[str, Any]] = None, debug: bool = False):
    """Create a graph and run a single propagate cycle."""
    graph = create_graph(config=config, debug=debug)
    return graph.propagate(instrument, trade_date)

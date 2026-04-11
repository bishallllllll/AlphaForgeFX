"""Workbench Part 4: agent tool wrappers for notebook debugging."""

from __future__ import annotations

from typing import Any, Callable, Dict

from tradingagents.agents.utils.core_stock_tools import get_stock_data
from tradingagents.agents.utils.technical_indicators_tools import get_indicators
from tradingagents.agents.utils.fundamental_data_tools import (
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement,
)
from tradingagents.agents.utils.news_data_tools import (
    get_news,
    get_global_news,
    get_insider_transactions,
)

TOOL_REGISTRY: Dict[str, Any] = {
    "get_stock_data": get_stock_data,
    "get_indicators": get_indicators,
    "get_fundamentals": get_fundamentals,
    "get_balance_sheet": get_balance_sheet,
    "get_cashflow": get_cashflow,
    "get_income_statement": get_income_statement,
    "get_news": get_news,
    "get_global_news": get_global_news,
    "get_insider_transactions": get_insider_transactions,
}


def list_tools() -> list[str]:
    """Return all tool names exposed by this layer."""
    return sorted(TOOL_REGISTRY.keys())


def get_tool(name: str) -> Any:
    """Fetch a tool object by name."""
    if name not in TOOL_REGISTRY:
        raise KeyError(f"Unknown tool: {name}")
    return TOOL_REGISTRY[name]


def invoke_tool(name: str, payload: Dict[str, Any]):
    """Invoke a LangChain @tool using its .invoke interface."""
    tool = get_tool(name)
    return tool.invoke(payload)

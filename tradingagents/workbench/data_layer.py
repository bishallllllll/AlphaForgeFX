"""Workbench Part 3: dataflow provider routing helpers."""

from __future__ import annotations

from typing import Any, Dict, List

from tradingagents.dataflows.interface import VENDOR_METHODS, route_to_vendor


def list_methods() -> List[str]:
    """List all abstract data methods supported by the vendor router."""
    return sorted(VENDOR_METHODS.keys())


def list_method_vendors() -> Dict[str, List[str]]:
    """Return the available vendor backends for each abstract data method."""
    return {method: sorted(vendors.keys()) for method, vendors in VENDOR_METHODS.items()}


def call(method: str, *args: Any, **kwargs: Any):
    """Call a routed data method through the active config vendor selection."""
    return route_to_vendor(method, *args, **kwargs)

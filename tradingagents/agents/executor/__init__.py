"""
Phase 5: Executor Module - Order Execution and Position Management

This module handles:
- Order execution with realistic slippage simulation
- Position tracking and P&L management
- Trade journaling and performance analytics
- Market monitoring and invalidation detection
"""

from .executor import create_executor
from .order_executor import OrderExecutor, Order, OrderType, OrderSide, OrderStatus
from .position_manager import PositionManager, Position, PositionStatus, ClosureReason
from .trade_journal import TradeJournal, TradeRecord, TradeStats
from .market_monitor import MarketMonitor, MarketSession, MarketConditions, TrendDirection

__all__ = [
    "create_executor",
    "OrderExecutor",
    "Order",
    "OrderType",
    "OrderSide",
    "OrderStatus",
    "PositionManager",
    "Position",
    "PositionStatus",
    "ClosureReason",
    "TradeJournal",
    "TradeRecord",
    "TradeStats",
    "MarketMonitor",
    "MarketSession",
    "MarketConditions",
    "TrendDirection",
]

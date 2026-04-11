"""
Phase 5: Order Executor Node

Main orchestrator for Phase 5 execution and monitoring.
Receives Phase 4 risk-approved decisions and executes trades,
manages positions, and tracks P&L.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from .order_executor import OrderExecutor, OrderType, OrderSide
from .position_manager import PositionManager, ClosureReason
from .trade_journal import TradeJournal
from .market_monitor import MarketMonitor


def create_executor(llm, memory):
    """
    Create an executor node for Phase 5 execution and monitoring.
    
    Args:
        llm: Language model client (for analysis/decisions)
        memory: Memory system for past trades
        
    Returns:
        A function that executes state and returns updated state
    """
    
    # Initialize executor components
    executor_engine = OrderExecutor(
        account_balance=10000,
        leverage=50,
        spread=2,
    )
    
    position_mgr = PositionManager(account_balance=10000)
    trade_journal = TradeJournal()
    market_monitor = MarketMonitor()
    
    def executor_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate Phase 5 execution.
        
        INPUT from Phase 4:
        - final_risk_decision: Risk analysis text
        - risk_approval_status: APPROVED | APPROVED_WITH_ADJUSTMENTS | REJECTED
        - final_entry: Entry price
        - final_stop_loss: Stop loss price
        - final_position_size: Position size string (e.g., "1 micro lot")
        - risk_adjusted_signal: Final signal (STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL)
        - adjustment_reason: If adjusted
        
        OUTPUT:
        - execution_status: EXECUTED | REJECTED | INVALID
        - order_id: Unique order identifier
        - order_details: {entry_price, fill_price, quantity, slippage}
        - position_id: Tracking position ID
        - position_tracking: {entry, stop_loss, tp1, tp2, current, pnl}
        - execution_report: {reason, timestamp, metrics}
        - portfolio_stats: Account summary
        """
        
        # ===== STEP 1: Validate Risk Approval =====
        approval_status = state.get("risk_approval_status", "REJECTED")
        
        if approval_status not in ["APPROVED", "APPROVED_WITH_ADJUSTMENTS"]:
            return _build_rejection_response(state, "Trade rejected by risk manager")
        
        # ===== STEP 2: Extract Trade Parameters =====
        try:
            entry_price = float(state.get("final_entry", 0))
            stop_loss = float(state.get("final_stop_loss", 0))
            position_size_str = state.get("final_position_size", "1 micro lot")
            signal = state.get("risk_adjusted_signal", "HOLD")
            pair = state.get("instrument", "EURUSD")
            
            # Parse position size (e.g., "1 micro lot" -> 1000 units)
            quantity = _parse_position_size(position_size_str)
            
            if quantity <= 0:
                return _build_rejection_response(state, "Invalid position size")
            
            # Determine trade direction from signal
            direction = "LONG" if signal in ["STRONG_BUY", "BUY"] else "SHORT"
            
        except Exception as e:
            return _build_rejection_response(state, f"Parameter parsing error: {str(e)}")
        
        # ===== STEP 3: Calculate Take Profit Levels =====
        # Based on risk/reward ratio
        risk_pips = abs(entry_price - stop_loss) / 0.0001
        
        # Assume 1:1.5 risk/reward ratio for TP
        tp_distance_pips = risk_pips * 1.5
        
        if direction == "LONG":
            take_profit_1 = entry_price + (risk_pips * 0.0001)      # 1:1 at first TP
            take_profit_2 = entry_price + (tp_distance_pips * 0.0001)  # 1:1.5 at second TP
        else:  # SHORT
            take_profit_1 = entry_price - (risk_pips * 0.0001)
            take_profit_2 = entry_price - (tp_distance_pips * 0.0001)
        
        # ===== STEP 4: Validate Order =====
        current_price = state.get("current_price", entry_price)
        margin_available, margin_msg = position_mgr.validate_margin(quantity)
        
        if not margin_available:
            return _build_rejection_response(state, margin_msg)
        
        # ===== STEP 5: Create and Execute Order =====
        conviction = state.get("conviction_level", "Unknown")
        signal_strength = state.get("trading_signal", signal)
        
        order = executor_engine.create_order(
            pair=pair,
            side=OrderSide.BUY if direction == "LONG" else OrderSide.SELL,
            quantity=quantity,
            entry_price=entry_price,
            order_type=OrderType.MARKET,
            conviction_level=conviction,
            reason=f"Phase 4 approved trade: {signal}",
        )
        
        # Simulate execution
        volatility = 50  # Default: normal conditions
        success, error_msg, filled_order = executor_engine.execute_order(
            order,
            current_price,
            volatility,
        )
        
        if not success:
            return _build_rejection_response(state, f"Order execution failed: {error_msg}")
        
        # ===== STEP 6: Open Position =====
        position = position_mgr.open_position(
            pair=pair,
            direction=direction,
            quantity=quantity,
            entry_price=filled_order.fill_price,
            stop_loss=stop_loss,
            take_profit_1=take_profit_1,
            take_profit_2=take_profit_2,
            conviction_level=conviction,
            signal_strength=signal_strength,
            macro_context=state.get("macro_report", ""),
            reason=f"Phase 4 approved: {signal}",
        )
        
        # ===== STEP 7: Log Trade =====
        trade_record = trade_journal.log_entry(
            trade_id=position.position_id,
            pair=pair,
            direction=direction,
            entry_price=filled_order.fill_price,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit_1,
            conviction_level=conviction,
            signal_strength=signal_strength,
            macro_context=state.get("macro_report", ""),
        )
        
        # ===== STEP 8: Update Market Monitor =====
        price_history = state.get("price_history", [filled_order.fill_price])
        market_conditions = market_monitor.update_market_conditions(
            pair=pair,
            current_price=current_price,
            price_history=price_history,
        )
        
        # ===== STEP 9: Build Response =====
        portfolio_stats = position_mgr.get_portfolio_stats()
        
        execution_response = {
            # Execution Status
            "execution_status": "EXECUTED",
            "execution_timestamp": datetime.utcnow().isoformat(),
            
            # Order Details
            "order_id": filled_order.order_id,
            "order_details": {
                "entry_price": float(filled_order.entry_price),
                "fill_price": float(filled_order.fill_price),
                "quantity": filled_order.quantity,
                "slippage_pips": round(filled_order.slippage_pips, 2),
                "side": filled_order.side.value,
            },
            
            # Position Details
            "position_id": position.position_id,
            "position_tracking": {
                "entry_price": float(position.entry_price),
                "stop_loss": float(position.stop_loss),
                "take_profit_1": float(position.take_profit_1),
                "take_profit_2": float(position.take_profit_2),
                "current_price": current_price,
                "direction": position.direction,
                "quantity": position.quantity,
                "margin_used": round(
                    (position.quantity / 1000) * 10000 * 0.02, 2
                ),
            },
            
            # P&L & Performance
            "unrealized_pnl_pips": 0,  # Just opened
            "unrealized_pnl_usd": 0,
            "execution_quality": round(100 - (filled_order.slippage_pips * 10), 1),  # Higher is better
            
            # Market Context
            "market_conditions": {
                "volatility": round(market_conditions.overall_volatility, 1),
                "average_spread": round(market_conditions.avg_spread, 1),
                "active_sessions": [s.value for s in market_conditions.sessions_open],
                "trend": market_conditions.trending.value,
            },
            
            # Account Status
            "portfolio_stats": {
                "open_positions": portfolio_stats["open_positions"],
                "margin_used": round(portfolio_stats["margin_used"], 2),
                "margin_available": round(portfolio_stats["margin_available"], 2),
                "margin_usage_percent": round(portfolio_stats["margin_usage_percent"], 1),
                "total_unrealized_pnl": round(portfolio_stats["unrealized_pnl_usd"], 2),
                "account_equity": round(portfolio_stats["account_equity"], 2),
            },
            
            # Journal Entry
            "trade_logged": True,
            "trade_id": trade_record.trade_id,
            
            # Risk Approval Status
            "risk_approval_status": approval_status,
            "adjustment_reason": state.get("adjustment_reason", "None"),
        }
        
        # Merge with original state
        updated_state = {**state, **execution_response}
        return updated_state
    
    return executor_node


def _build_rejection_response(state: Dict[str, Any], reason: str) -> Dict[str, Any]:
    """Build a rejection response."""
    return {
        **state,
        "execution_status": "REJECTED",
        "execution_timestamp": datetime.utcnow().isoformat(),
        "rejection_reason": reason,
    }


def _parse_position_size(size_str: str) -> float:
    """
    Parse position size string to units.
    
    Examples:
    - "1 micro lot" -> 1000 units
    - "0.5 micro lot" -> 500 units
    - "1000 units" -> 1000 units
    - "1 mini lot" -> 10000 units
    """
    size_str = size_str.lower().strip()
    
    if "micro" in size_str:
        amount = float(size_str.split()[0])
        return amount * 1000
    elif "mini" in size_str:
        amount = float(size_str.split()[0])
        return amount * 10000
    elif "standard" in size_str:
        amount = float(size_str.split()[0])
        return amount * 100000
    elif "units" in size_str:
        return float(size_str.split()[0])
    else:
        # Try to parse as number
        try:
            return float(size_str) * 1000  # Assume micro lots
        except ValueError:
            return 1000  # Default to 1 micro lot

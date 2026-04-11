"""
Phase 5: Position Manager

Manages all open positions including entry prices, stop-loss levels,
take-profit targets, and real-time P&L tracking. Handles partial exits
and position closure detection.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid


class PositionStatus(Enum):
    """Position lifecycle states."""
    OPEN = "OPEN"                  # Active position
    PARTIALLY_CLOSED = "PARTIALLY_CLOSED"
    CLOSED = "CLOSED"
    INVALIDATED = "INVALIDATED"    # Closed due to market condition change


class ClosureReason(Enum):
    """Why a position was closed."""
    TAKE_PROFIT_1 = "TAKE_PROFIT_1"
    TAKE_PROFIT_2 = "TAKE_PROFIT_2"
    STOP_LOSS = "STOP_LOSS"
    MANUAL = "MANUAL"
    INVALIDATION = "INVALIDATION"
    BREAKEVEN = "BREAKEVEN"


@dataclass
class Position:
    """Represents an open or closed position."""
    position_id: str
    pair: str                           # e.g., "EURUSD"
    direction: str                      # LONG or SHORT
    quantity: float                     # Units (1000 = 1 micro lot)
    
    # Entry details
    entry_price: float
    entry_time: datetime
    
    # Risk management levels
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    
    # Entry details (continued)
    entry_spread: float = 2             # Spread at entry
    
    # Exit tracking
    tp1_filled: bool = False
    tp1_exit_price: Optional[float] = None
    tp1_exit_time: Optional[datetime] = None
    tp1_quantity: float = 0             # How many units closed at TP1
    
    tp2_filled: bool = False
    tp2_exit_price: Optional[float] = None
    tp2_exit_time: Optional[datetime] = None
    tp2_quantity: float = 0             # How many units closed at TP2
    
    sl_hit: bool = False
    sl_exit_price: Optional[float] = None
    sl_exit_time: Optional[datetime] = None
    
    # Position sizing
    initial_quantity: float = 0         # Initial size (for partial close tracking)
    remaining_quantity: float = 0       # Still open
    
    # Current state
    current_price: Optional[float] = None
    status: PositionStatus = PositionStatus.OPEN
    closure_reason: Optional[ClosureReason] = None
    
    # P&L tracking
    unrealized_pnl_pips: float = 0
    unrealized_pnl_usd: float = 0
    realized_pnl_pips: float = 0
    realized_pnl_usd: float = 0
    
    # Metadata
    conviction_level: Optional[str] = None
    signal_strength: Optional[str] = None
    macro_context: Optional[str] = None
    reason: Optional[str] = None


class PositionManager:
    """Manages all active and closed positions."""
    
    MARGIN_REQUIREMENT = 0.02           # 2% per micro lot
    
    def __init__(self, account_balance: float = 10000):
        """
        Initialize position manager.
        
        Args:
            account_balance: Starting account balance in USD
        """
        self.account_balance = account_balance
        self.positions: Dict[str, Position] = {}
        self.closed_positions: List[Position] = []
        
        # Track totals
        self.total_margin_used = 0
        self.total_unrealized_pnl = 0

    def open_position(
        self,
        pair: str,
        direction: str,
        quantity: float,
        entry_price: float,
        stop_loss: float,
        take_profit_1: float,
        take_profit_2: float,
        conviction_level: Optional[str] = None,
        signal_strength: Optional[str] = None,
        macro_context: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Position:
        """
        Open a new position.
        
        Args:
            pair: Currency pair
            direction: LONG or SHORT
            quantity: Quantity in units
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit_1: First TP level (50% exit)
            take_profit_2: Second TP level (50% exit)
            conviction_level: From Phase 3 trader
            signal_strength: From Phase 3 trader
            macro_context: From Phase 1 macro analyst
            reason: Why position was opened
            
        Returns:
            Newly opened Position
        """
        position_id = str(uuid.uuid4())[:8]
        
        position = Position(
            position_id=position_id,
            pair=pair,
            direction=direction,
            quantity=quantity,
            initial_quantity=quantity,
            remaining_quantity=quantity,
            entry_price=entry_price,
            entry_time=datetime.utcnow(),
            stop_loss=stop_loss,
            take_profit_1=take_profit_1,
            take_profit_2=take_profit_2,
            conviction_level=conviction_level,
            signal_strength=signal_strength,
            macro_context=macro_context,
            reason=reason,
        )
        
        self.positions[position_id] = position
        self._update_margin_usage()
        
        return position

    def update_position_prices(
        self,
        pair: str,
        current_price: float,
    ) -> Dict[str, Position]:
        """
        Update all positions for a pair with current price.
        
        Args:
            pair: Currency pair
            current_price: Current market price
            
        Returns:
            Dictionary of positions for this pair
        """
        pair_positions = {}
        
        for pos_id, position in list(self.positions.items()):
            if position.pair != pair or position.status == PositionStatus.CLOSED:
                continue
            
            position.current_price = current_price
            self._calculate_pnl(position)
            pair_positions[pos_id] = position
            
            # Check for closure conditions
            self._check_closure_conditions(position)
        
        self._update_margin_usage()
        return pair_positions

    def close_position(
        self,
        position_id: str,
        exit_price: float,
        reason: ClosureReason,
    ) -> Optional[Position]:
        """
        Fully close a position.
        
        Args:
            position_id: Position to close
            exit_price: Exit price
            reason: Why it's being closed
            
        Returns:
            Closed Position or None if not found
        """
        position = self.positions.get(position_id)
        if not position:
            return None
        
        # Record closure
        position.status = PositionStatus.CLOSED
        position.closure_reason = reason
        
        if reason == ClosureReason.TAKE_PROFIT_1:
            position.tp1_filled = True
            position.tp1_exit_price = exit_price
            position.tp1_exit_time = datetime.utcnow()
            position.tp1_quantity = position.remaining_quantity
            position.remaining_quantity = 0
        elif reason == ClosureReason.TAKE_PROFIT_2:
            position.tp2_filled = True
            position.tp2_exit_price = exit_price
            position.tp2_exit_time = datetime.utcnow()
            position.tp2_quantity = position.remaining_quantity
            position.remaining_quantity = 0
        elif reason == ClosureReason.STOP_LOSS:
            position.sl_hit = True
            position.sl_exit_price = exit_price
            position.sl_exit_time = datetime.utcnow()
            position.remaining_quantity = 0
        else:
            position.remaining_quantity = 0
        
        # Calculate realized P&L
        self._calculate_realized_pnl(position, exit_price)
        
        # Move to closed list
        self.closed_positions.append(position)
        del self.positions[position_id]
        self._update_margin_usage()
        
        return position

    def close_partial(
        self,
        position_id: str,
        quantity: float,
        exit_price: float,
        reason: ClosureReason,
    ) -> Optional[Position]:
        """
        Partially close a position (for TP1 partial exits).
        
        Args:
            position_id: Position to close
            quantity: Quantity to close (rest remains open)
            exit_price: Exit price
            reason: Why closed (usually TAKE_PROFIT_1)
            
        Returns:
            Updated Position or None
        """
        position = self.positions.get(position_id)
        if not position:
            return None
        
        if quantity > position.remaining_quantity:
            quantity = position.remaining_quantity
        
        # Record partial closure
        if reason == ClosureReason.TAKE_PROFIT_1:
            position.tp1_filled = True
            position.tp1_exit_price = exit_price
            position.tp1_exit_time = datetime.utcnow()
            position.tp1_quantity = quantity
        
        # Calculate P&L on closed portion
        pips = self._calculate_pips(position, exit_price)
        pnl_usd = self._pips_to_usd(pips, quantity)
        
        position.realized_pnl_pips += pips
        position.realized_pnl_usd += pnl_usd
        position.remaining_quantity -= quantity
        
        if position.remaining_quantity <= 0:
            position.status = PositionStatus.CLOSED
            position.closure_reason = reason
            self.closed_positions.append(position)
            del self.positions[position_id]
        else:
            position.status = PositionStatus.PARTIALLY_CLOSED
        
        self._update_margin_usage()
        return position

    def _check_closure_conditions(self, position: Position) -> None:
        """Check if position should be auto-closed based on price levels."""
        if not position.current_price:
            return
        
        # LONG positions
        if position.direction == "LONG":
            # Check TP2 first (complete exit)
            if not position.tp2_filled and position.current_price >= position.take_profit_2:
                # Auto-close at TP2
                pass  # Will be handled by monitoring loop
            
            # Check TP1 (partial exit)
            elif not position.tp1_filled and position.current_price >= position.take_profit_1:
                # Auto-partial close at TP1
                pass
            
            # Check SL
            elif not position.sl_hit and position.current_price <= position.stop_loss:
                # Auto-close at SL
                pass
        
        # SHORT positions
        elif position.direction == "SHORT":
            # Check TP2 first
            if not position.tp2_filled and position.current_price <= position.take_profit_2:
                pass
            
            # Check TP1
            elif not position.tp1_filled and position.current_price <= position.take_profit_1:
                pass
            
            # Check SL
            elif not position.sl_hit and position.current_price >= position.stop_loss:
                pass

    def _calculate_pnl(self, position: Position) -> None:
        """Calculate unrealized P&L for a position."""
        if not position.current_price:
            return
        
        pips = self._calculate_pips(position, position.current_price)
        pnl_usd = self._pips_to_usd(pips, position.remaining_quantity)
        
        position.unrealized_pnl_pips = pips
        position.unrealized_pnl_usd = pnl_usd

    def _calculate_realized_pnl(self, position: Position, exit_price: float) -> None:
        """Calculate realized P&L when position closes."""
        pips = self._calculate_pips(position, exit_price)
        pnl_usd = self._pips_to_usd(pips, position.remaining_quantity)
        
        position.realized_pnl_pips = pips
        position.realized_pnl_usd = pnl_usd

    def _calculate_pips(self, position: Position, price: float) -> float:
        """Calculate pips difference."""
        price_diff = price - position.entry_price
        pips = price_diff / 0.0001
        
        # SHORT positions: invert pips
        if position.direction == "SHORT":
            pips = -pips
        
        return pips

    def _pips_to_usd(self, pips: float, quantity: float) -> float:
        """Convert pips to USD (1 pip = $0.10 per micro lot)."""
        micro_lots = quantity / 1000
        return pips * 0.10 * micro_lots

    def _update_margin_usage(self) -> None:
        """Update total margin used."""
        total_margin = 0
        for position in self.positions.values():
            if position.status != PositionStatus.CLOSED:
                micro_lots = position.remaining_quantity / 1000
                margin = micro_lots * self.account_balance * self.MARGIN_REQUIREMENT
                total_margin += margin
        
        self.total_margin_used = total_margin
        self.total_unrealized_pnl = sum(
            p.unrealized_pnl_usd for p in self.positions.values()
        )

    def get_active_positions(self) -> List[Position]:
        """Get all active positions."""
        return [
            p for p in self.positions.values()
            if p.status in [PositionStatus.OPEN, PositionStatus.PARTIALLY_CLOSED]
        ]

    def get_exposure(self, pair: str) -> float:
        """Get total open quantity for a pair."""
        total = 0
        for pos in self.get_active_positions():
            if pos.pair == pair:
                total += pos.remaining_quantity
        return total

    def validate_margin(self, new_position_units: float) -> tuple[bool, Optional[str]]:
        """Check if there's enough margin for a new position."""
        micro_lots = new_position_units / 1000
        margin_required = micro_lots * self.account_balance * self.MARGIN_REQUIREMENT
        margin_available = self.account_balance - self.total_margin_used
        
        if margin_required > margin_available:
            return False, (
                f"Insufficient margin: need ${margin_required:.2f}, "
                f"have ${margin_available:.2f}"
            )
        
        return True, None

    def get_portfolio_stats(self) -> Dict[str, Any]:
        """Get overall portfolio statistics."""
        active = self.get_active_positions()
        
        total_unrealized = sum(p.unrealized_pnl_usd for p in active)
        total_realized = sum(p.realized_pnl_usd for p in self.closed_positions)
        
        weight = {}
        for pos in active:
            micro_lots = pos.remaining_quantity / 1000
            margin = micro_lots * self.account_balance * self.MARGIN_REQUIREMENT
            weight[pos.pair] = (margin / self.account_balance) * 100 if self.account_balance else 0
        
        return {
            "open_positions": len(active),
            "margin_used": self.total_margin_used,
            "margin_available": self.account_balance - self.total_margin_used,
            "margin_usage_percent": (self.total_margin_used / self.account_balance * 100) if self.account_balance else 0,
            "unrealized_pnl_usd": total_unrealized,
            "unrealized_pnl_percent": (total_unrealized / self.account_balance * 100) if self.account_balance else 0,
            "realized_pnl_usd": total_realized,
            "total_pnl_usd": total_unrealized + total_realized,
            "account_equity": self.account_balance + total_unrealized + total_realized,
            "position_weights": weight,
            "closed_positions": len(self.closed_positions),
        }

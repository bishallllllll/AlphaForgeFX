"""
Phase 5: Order Execution Engine

Converts Phase 4 approved trading decisions into executable orders,
simulates order fills with realistic spreads/slippage, and tracks
order lifecycle from creation to execution.

Default Configuration:
- Account Balance: $10,000 USD
- Leverage: 50:1
- Spread: 2 pips (EUR/USD)
- Slippage: 0-5 pips based on volatility
- Lot Size: Micro lot (1,000 units)
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


class OrderType(Enum):
    """Order execution types."""
    MARKET = "MARKET"          # Execute immediately at market price
    LIMIT = "LIMIT"            # Execute only at specified price
    STOP = "STOP"              # Execute when price reaches stop level


class OrderSide(Enum):
    """Order direction."""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(Enum):
    """Order lifecycle states."""
    PENDING = "PENDING"                    # Awaiting execution
    FILLED = "FILLED"                      # Fully executed
    PARTIALLY_FILLED = "PARTIALLY_FILLED"  # Partial execution
    CANCELLED = "CANCELLED"                # User cancelled
    REJECTED = "REJECTED"                  # Broker rejected
    EXPIRED = "EXPIRED"                    # Order expired


@dataclass
class Order:
    """Represents a single forex order."""
    order_id: str
    pair: str                          # e.g., "EURUSD"
    order_type: OrderType
    side: OrderSide                    # BUY or SELL
    quantity: float                    # in units (1000 = 1 micro lot)
    
    # Pricing
    entry_price: Optional[float] = None        # Expected entry price
    limit_price: Optional[float] = None        # For LIMIT orders
    stop_price: Optional[float] = None         # For STOP orders
    
    # Execution
    fill_price: Optional[float] = None         # Actual execution price
    filled_quantity: float = 0                 # Actual filled quantity
    status: OrderStatus = OrderStatus.PENDING
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    filled_at: Optional[datetime] = None
    
    # Metadata
    slippage_pips: float = 0                   # Difference between expected and actual
    spread_at_execution: float = 2             # Spread when order executed
    conviction_level: Optional[str] = None     # From Phase 3 trader decision
    reason: Optional[str] = None               # Why this order was placed


class OrderExecutor:
    """Executes orders with realistic slippage simulation."""
    
    # Default configuration
    DEFAULT_LEVERAGE = 50
    DEFAULT_SPREAD = 2                  # pips
    DEFAULT_ACCOUNT_BALANCE = 10000     # USD
    MAX_POSITION_SIZE = 5               # max simultaneous positions
    MARGIN_REQUIREMENT = 0.02           # 2% per micro lot
    
    def __init__(
        self,
        account_balance: float = DEFAULT_ACCOUNT_BALANCE,
        leverage: int = DEFAULT_LEVERAGE,
        spread: float = DEFAULT_SPREAD,
    ):
        """
        Initialize order executor with account parameters.
        
        Args:
            account_balance: Starting USD balance
            leverage: Leverage ratio (50:1 default)
            spread: Default spread in pips (2 pips EUR/USD typical)
        """
        self.account_balance = account_balance
        self.leverage = leverage
        self.spread = spread
        self.buying_power = account_balance * leverage
        
        self.executed_orders: Dict[str, Order] = {}
        self.order_history = []

    def create_order(
        self,
        pair: str,
        side: OrderSide,
        quantity: float,
        entry_price: float,
        order_type: OrderType = OrderType.MARKET,
        conviction_level: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Order:
        """
        Create a new order.
        
        Args:
            pair: Currency pair (e.g., "EURUSD")
            side: BUY or SELL
            quantity: Quantity in units
            entry_price: Expected entry price
            order_type: MARKET, LIMIT, or STOP
            conviction_level: Conviction from Phase 3 decision
            reason: Reason for trade (technical, macro, etc.)
            
        Returns:
            Order object with unique order_id
        """
        order_id = str(uuid.uuid4())[:8]
        
        order = Order(
            order_id=order_id,
            pair=pair,
            order_type=order_type,
            side=side,
            quantity=quantity,
            entry_price=entry_price,
            conviction_level=conviction_level,
            reason=reason,
        )
        
        return order

    def validate_order(
        self,
        order: Order,
        current_price: float,
        margin_used: float = 0,
    ) -> tuple[bool, Optional[str]]:
        """
        Validate order before execution.
        
        Args:
            order: Order to validate
            current_price: Current market price
            margin_used: Current margin used (from other positions)
            
        Returns:
            (is_valid, rejection_reason)
        """
        errors = []
        
        # Validate quantity
        if order.quantity <= 0:
            errors.append(f"Invalid quantity: {order.quantity}")
        
        # Validate price
        if order.entry_price is None or order.entry_price <= 0:
            errors.append(f"Invalid price: {order.entry_price}")
        
        # Check margin availability
        margin_per_micro_lot = self.account_balance * self.MARGIN_REQUIREMENT
        margin_required = (order.quantity / 1000) * margin_per_micro_lot
        total_margin = margin_used + margin_required
        
        if total_margin > self.account_balance:
            errors.append(
                f"Insufficient margin: need {margin_required}, "
                f"have {self.account_balance - margin_used}"
            )
        
        # Validate price reasonableness (should be within 50 pips of current)
        price_diff = abs(current_price - order.entry_price)
        price_diff_pips = price_diff / 0.0001
        if price_diff_pips > 50:
            errors.append(
                f"Entry price too far from market: "
                f"{price_diff_pips} pips away"
            )
        
        is_valid = len(errors) == 0
        rejection_reason = "; ".join(errors) if errors else None
        
        return is_valid, rejection_reason

    def calculate_slippage(
        self,
        volatility: float = 50,  # 0-100 scale
        order_type: OrderType = OrderType.MARKET,
    ) -> float:
        """
        Calculate realistic slippage based on volatility.
        
        Args:
            volatility: Market volatility 0-100
            order_type: MARKET orders have more slippage than LIMIT
            
        Returns:
            Slippage in pips
        """
        # Base slippage from spread
        if order_type == OrderType.MARKET:
            # MARKET orders: 1-5 pips depending on volatility
            slippage = self.spread + (volatility / 20)  # 0-5 pips range
        elif order_type == OrderType.LIMIT:
            # LIMIT orders: 0-2 pips slippage
            slippage = volatility / 50  # 0-2 pips range
        else:  # STOP
            # STOP orders: 2-8 pips slippage (worse due to gap risk)
            slippage = self.spread + (volatility / 12)
        
        return min(max(slippage, 0), 10)  # Clamp to 0-10 pips

    def execute_order(
        self,
        order: Order,
        current_price: float,
        volatility: float = 50,
    ) -> tuple[bool, Optional[str], Order]:
        """
        Execute order with realistic fill simulation.
        
        Args:
            order: Order to execute
            current_price: Current market price
            volatility: Market volatility (0-100)
            
        Returns:
            (success, error_message, updated_order)
        """
        # Validate order first
        is_valid, rejection_reason = self.validate_order(order, current_price)
        if not is_valid:
            order.status = OrderStatus.REJECTED
            return False, rejection_reason, order
        
        # Calculate slippage
        slippage_pips = self.calculate_slippage(volatility, order.order_type)
        
        # Simulate fill price
        fill_price = self._simulate_fill(
            current_price,
            order.side,
            slippage_pips,
        )
        
        # Update order with execution details
        order.fill_price = fill_price
        order.filled_quantity = order.quantity
        order.status = OrderStatus.FILLED
        order.filled_at = datetime.utcnow()
        order.slippage_pips = slippage_pips
        
        # Store order
        self.executed_orders[order.order_id] = order
        self.order_history.append(order)
        
        return True, None, order

    def _simulate_fill(
        self,
        current_price: float,
        side: OrderSide,
        slippage_pips: float,
    ) -> float:
        """
        Simulate realistic fill price with slippage.
        
        Args:
            current_price: Market price
            side: BUY or SELL
            slippage_pips: Slippage in pips
            
        Returns:
            Simulated fill price
        """
        slippage_price = (slippage_pips * 0.0001)
        
        # BUY orders: slippage means buying higher (negative for seller)
        # SELL orders: slippage means selling lower
        if side == OrderSide.BUY:
            fill_price = current_price + slippage_price
        else:
            fill_price = current_price - slippage_price
        
        return fill_price

    def get_order_cost_usd(self, order: Order) -> float:
        """Calculate USD cost/margin for an order."""
        # Each micro lot = 1,000 units
        micro_lots = order.quantity / 1000
        margin_per_lot = self.account_balance * self.MARGIN_REQUIREMENT
        return micro_lots * margin_per_lot

    def get_order_pnl(self, order: Order, current_price: float) -> float:
        """Calculate unrealized P&L for an order in pips."""
        if order.status != OrderStatus.FILLED or not order.fill_price:
            return 0
        
        price_diff = current_price - order.fill_price
        pips = price_diff / 0.0001
        
        if order.side == OrderSide.SELL:
            pips = -pips
        
        return pips

    def get_order_pnl_usd(self, order: Order, current_price: float) -> float:
        """Calculate unrealized P&L for an order in USD."""
        pips = self.get_order_pnl(order, current_price)
        
        # Each micro lot = 1,000 units
        # 1 pip = $0.10 per micro lot
        micro_lots = order.quantity / 1000
        pnl_usd = pips * 0.10 * micro_lots
        
        return pnl_usd

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get statistics on executed orders."""
        if not self.executed_orders:
            return {
                "total_orders": 0,
                "filled_orders": 0,
                "rejected_orders": 0,
                "avg_slippage_pips": 0,
            }
        
        filled = [o for o in self.executed_orders.values() if o.status == OrderStatus.FILLED]
        rejected = [o for o in self.executed_orders.values() if o.status == OrderStatus.REJECTED]
        
        avg_slippage = (
            sum(o.slippage_pips for o in filled) / len(filled)
            if filled else 0
        )
        
        return {
            "total_orders": len(self.executed_orders),
            "filled_orders": len(filled),
            "rejected_orders": len(rejected),
            "avg_slippage_pips": round(avg_slippage, 2),
            "fill_rate": round((len(filled) / len(self.executed_orders) * 100), 1),
        }

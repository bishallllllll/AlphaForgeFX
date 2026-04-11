"""
Phase 5: Trade Journal & P&L Tracker

Records complete trade lifecycle from entry to exit,
calculates performance metrics, and provides analytics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import csv
import json


@dataclass
class TradeRecord:
    """Complete record of a single trade."""
    trade_id: str
    pair: str
    direction: str                      # LONG or SHORT
    
    # Entry
    entry_price: float
    entry_time: datetime
    entry_spread: float = 2
    
    # Exit
    exit_price: float = 0
    exit_time: Optional[datetime] = None
    exit_reason: Optional[str] = None   # TP1, TP2, SL, MANUAL, INVALIDATION
    
    # Position details
    quantity: float = 0                 # Units entered
    partially_closed: bool = False
    partial_quantity: float = 0         # Quantity closed at TP1
    
    # P&L
    pnl_pips: float = 0
    pnl_usd: float = 0
    
    # Risk metrics
    risk_pips: float = 0                # Distance to SL
    reward_pips: float = 0              # Distance to target
    risk_reward_ratio: float = 0
    achieved_risk_reward: float = 0
    
    # Metadata
    conviction_level: Optional[str] = None
    signal_strength: Optional[str] = None
    macro_context: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Duration
    duration_seconds: int = 0
    duration_minutes: int = 0
    duration_hours: int = 0


@dataclass
class TradeStats:
    """Trading performance statistics."""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    breakeven_trades: int = 0
    
    win_rate: float = 0                 # Percent
    loss_rate: float = 0
    
    avg_win_pips: float = 0
    avg_loss_pips: float = 0
    avg_win_usd: float = 0
    avg_loss_usd: float = 0
    
    largest_win_pips: float = 0
    largest_loss_pips: float = 0
    
    profit_factor: float = 0            # Total wins / Total losses
    
    total_pnl_pips: float = 0
    total_pnl_usd: float = 0
    
    avg_duration_minutes: float = 0
    
    best_day_pnl: float = 0
    worst_day_pnl: float = 0
    
    # Risk metrics
    risk_reward_avg: float = 0
    achieved_rr_avg: float = 0


class TradeJournal:
    """Manages trade records and calculates statistics."""
    
    def __init__(self):
        """Initialize trade journal."""
        self.trades: List[TradeRecord] = []
        self.stats = TradeStats()

    def log_entry(
        self,
        trade_id: str,
        pair: str,
        direction: str,
        entry_price: float,
        quantity: float,
        stop_loss: float,
        take_profit: float,
        conviction_level: Optional[str] = None,
        signal_strength: Optional[str] = None,
        macro_context: Optional[str] = None,
    ) -> TradeRecord:
        """
        Create a trade entry record.
        
        Args:
            trade_id: Unique trade ID
            pair: Currency pair
            direction: LONG or SHORT
            entry_price: Entry price
            quantity: Quantity in units
            stop_loss: SL price
            take_profit: TP price
            conviction_level: From Phase 3
            signal_strength: From Phase 3
            macro_context: From Phase 1
            
        Returns:
            TradeRecord
        """
        # Calculate initial risk/reward
        if direction == "LONG":
            risk_pips = (entry_price - stop_loss) / 0.0001
            reward_pips = (take_profit - entry_price) / 0.0001
        else:  # SHORT
            risk_pips = (stop_loss - entry_price) / 0.0001
            reward_pips = (entry_price - take_profit) / 0.0001
        
        risk_reward = reward_pips / risk_pips if risk_pips > 0 else 0
        
        trade = TradeRecord(
            trade_id=trade_id,
            pair=pair,
            direction=direction,
            entry_price=entry_price,
            entry_time=datetime.utcnow(),
            quantity=quantity,
            risk_pips=risk_pips,
            reward_pips=reward_pips,
            risk_reward_ratio=risk_reward,
            conviction_level=conviction_level,
            signal_strength=signal_strength,
            macro_context=macro_context,
        )
        
        self.trades.append(trade)
        return trade

    def log_exit(
        self,
        trade_id: str,
        exit_price: float,
        exit_reason: str,
        partial_closure: bool = False,
        partial_quantity: float = 0,
    ) -> Optional[TradeRecord]:
        """
        Record trade exit.
        
        Args:
            trade_id: Trade to close
            exit_price: Exit price
            exit_reason: TP1, TP2, SL, MANUAL, INVALIDATION
            partial_closure: Is this a partial exit?
            partial_quantity: If partial, how many units closed
            
        Returns:
            Updated TradeRecord or None
        """
        trade = self._find_trade(trade_id)
        if not trade:
            return None
        
        trade.exit_price = exit_price
        trade.exit_time = datetime.utcnow()
        trade.exit_reason = exit_reason
        
        if partial_closure:
            trade.partially_closed = True
            trade.partial_quantity = partial_quantity
            qty = partial_quantity
        else:
            qty = trade.quantity
        
        # Calculate P&L
        self._calculate_pnl(trade, qty)
        
        # Calculate duration
        if trade.exit_time and trade.entry_time:
            duration = (trade.exit_time - trade.entry_time).total_seconds()
            trade.duration_seconds = int(duration)
            trade.duration_minutes = int(duration / 60)
            trade.duration_hours = int(duration / 3600)
        
        return trade

    def _calculate_pnl(self, trade: TradeRecord, quantity: float) -> None:
        """Calculate P&L for a trade."""
        price_diff = trade.exit_price - trade.entry_price
        
        if trade.direction == "SHORT":
            price_diff = -price_diff
        
        pips = price_diff / 0.0001
        
        # Each micro lot: 1 pip = $0.10
        micro_lots = quantity / 1000
        pnl_usd = pips * 0.10 * micro_lots
        
        trade.pnl_pips = pips
        trade.pnl_usd = pnl_usd
        
        # Calculate achieved RR
        if trade.risk_pips > 0:
            trade.achieved_risk_reward = pips / trade.risk_pips

    def _find_trade(self, trade_id: str) -> Optional[TradeRecord]:
        """Find trade by ID."""
        for trade in self.trades:
            if trade.trade_id == trade_id:
                return trade
        return None

    def calculate_stats(self) -> TradeStats:
        """Calculate all trading statistics."""
        if not self.trades:
            return TradeStats()
        
        stats = TradeStats()
        stats.total_trades = len(self.trades)
        
        # Categorize trades
        winners = [t for t in self.trades if t.pnl_pips > 0 and t.exit_time]
        losers = [t for t in self.trades if t.pnl_pips < 0 and t.exit_time]
        breakeven = [t for t in self.trades if t.pnl_pips == 0 and t.exit_time]
        
        stats.winning_trades = len(winners)
        stats.losing_trades = len(losers)
        stats.breakeven_trades = len(breakeven)
        
        completed = len(winners) + len(losers) + len(breakeven)
        if completed > 0:
            stats.win_rate = (stats.winning_trades / completed) * 100
            stats.loss_rate = (stats.losing_trades / completed) * 100
        
        # Win/Loss metrics
        if winners:
            stats.avg_win_pips = sum(t.pnl_pips for t in winners) / len(winners)
            stats.avg_win_usd = sum(t.pnl_usd for t in winners) / len(winners)
            stats.largest_win_pips = max(t.pnl_pips for t in winners)
        
        if losers:
            stats.avg_loss_pips = sum(t.pnl_pips for t in losers) / len(losers)
            stats.avg_loss_usd = sum(t.pnl_usd for t in losers) / len(losers)
            stats.largest_loss_pips = min(t.pnl_pips for t in losers)
        
        # Profit factor
        total_wins = sum(t.pnl_usd for t in winners)
        total_losses = abs(sum(t.pnl_usd for t in losers))
        stats.profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        # Total P&L
        stats.total_pnl_pips = sum(t.pnl_pips for t in self.trades if t.exit_time)
        stats.total_pnl_usd = sum(t.pnl_usd for t in self.trades if t.exit_time)
        
        # Duration
        durations = [t.duration_minutes for t in self.trades if t.exit_time and t.duration_minutes]
        if durations:
            stats.avg_duration_minutes = sum(durations) / len(durations)
        
        # Risk/Reward
        rrs = [t.risk_reward_ratio for t in self.trades if t.risk_reward_ratio > 0]
        if rrs:
            stats.risk_reward_avg = sum(rrs) / len(rrs)
        
        achieved_rrs = [t.achieved_risk_reward for t in self.trades if t.exit_time]
        if achieved_rrs:
            stats.achieved_rr_avg = sum(achieved_rrs) / len(achieved_rrs)
        
        self.stats = stats
        return stats

    def get_stats_by_pair(self, pair: str) -> TradeStats:
        """Get statistics for a specific pair."""
        pair_trades = [t for t in self.trades if t.pair == pair]
        
        stats = TradeStats()
        stats.total_trades = len(pair_trades)
        
        winners = [t for t in pair_trades if t.pnl_pips > 0 and t.exit_time]
        losers = [t for t in pair_trades if t.pnl_pips < 0 and t.exit_time]
        
        stats.winning_trades = len(winners)
        stats.losing_trades = len(losers)
        
        if stats.total_trades > 0:
            stats.win_rate = (stats.winning_trades / stats.total_trades) * 100
        
        if winners:
            stats.avg_win_pips = sum(t.pnl_pips for t in winners) / len(winners)
        if losers:
            stats.avg_loss_pips = sum(t.pnl_pips for t in losers) / len(losers)
        
        stats.total_pnl_pips = sum(t.pnl_pips for t in pair_trades if t.exit_time)
        stats.total_pnl_usd = sum(t.pnl_usd for t in pair_trades if t.exit_time)
        
        return stats

    def export_csv(self, filepath: str) -> None:
        """Export trade journal to CSV."""
        if not self.trades:
            return
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            headers = [
                'trade_id', 'pair', 'direction', 'entry_price', 'exit_price',
                'quantity', 'pnl_pips', 'pnl_usd', 'exit_reason', 'duration_minutes',
                'conviction_level', 'signal_strength'
            ]
            writer.writerow(headers)
            
            # Rows
            for trade in self.trades:
                if not trade.exit_time:
                    continue
                
                writer.writerow([
                    trade.trade_id,
                    trade.pair,
                    trade.direction,
                    f"{trade.entry_price:.4f}",
                    f"{trade.exit_price:.4f}",
                    int(trade.quantity),
                    f"{trade.pnl_pips:.1f}",
                    f"{trade.pnl_usd:.2f}",
                    trade.exit_reason,
                    trade.duration_minutes,
                    trade.conviction_level or "",
                    trade.signal_strength or "",
                ])

    def export_json(self, filepath: str) -> None:
        """Export trade journal to JSON."""
        trades_data = []
        for trade in self.trades:
            trades_data.append({
                'trade_id': trade.trade_id,
                'pair': trade.pair,
                'direction': trade.direction,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price if trade.exit_time else None,
                'pnl_pips': trade.pnl_pips,
                'pnl_usd': trade.pnl_usd,
                'exit_reason': trade.exit_reason,
                'duration_minutes': trade.duration_minutes,
                'conviction_level': trade.conviction_level,
                'signal_strength': trade.signal_strength,
            })
        
        stats_data = {
            'total_trades': self.stats.total_trades,
            'winning_trades': self.stats.winning_trades,
            'losing_trades': self.stats.losing_trades,
            'win_rate': round(self.stats.win_rate, 2),
            'total_pnl_usd': round(self.stats.total_pnl_usd, 2),
            'profit_factor': round(self.stats.profit_factor, 2),
        }
        
        output = {
            'trades': trades_data,
            'stats': stats_data,
        }
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2, default=str)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics dictionary."""
        self.calculate_stats()
        return {
            'total_trades': self.stats.total_trades,
            'winning_trades': self.stats.winning_trades,
            'losing_trades': self.stats.losing_trades,
            'win_rate': f"{self.stats.win_rate:.1f}%",
            'total_pnl_usd': f"${self.stats.total_pnl_usd:.2f}",
            'total_pnl_pips': f"{self.stats.total_pnl_pips:.0f}",
            'avg_win_pips': f"{self.stats.avg_win_pips:.1f}",
            'avg_loss_pips': f"{self.stats.avg_loss_pips:.1f}",
            'profit_factor': f"{self.stats.profit_factor:.2f}",
            'avg_duration_minutes': f"{self.stats.avg_duration_minutes:.0f}",
        }

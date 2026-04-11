"""
Phase 5: Market Monitor

Tracks market sessions, volatility, spreads, and validates
positions for potential invalidation due to market condition changes.
"""

from dataclasses import dataclass
from enum import Enum
from datetime import datetime, time
from typing import Dict, List, Optional, Tuple
from typing import Dict, List, Optional, Tuple


class MarketSession(Enum):
    """Forex trading sessions."""
    TOKYO = "TOKYO"           # 20:00 UTC to 09:00 UTC (Sunday to Friday)
    LONDON = "LONDON"         # 08:00 UTC to 17:00 UTC
    NEW_YORK = "NEW_YORK"     # 13:00 UTC to 22:00 UTC
    SYDNEY = "SYDNEY"         # 21:00 UTC to 06:00 UTC


class TrendDirection(Enum):
    """Market trend direction."""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    SIDEWAYS = "SIDEWAYS"


@dataclass
class SessionState:
    """State of a trading session."""
    session: MarketSession
    utc_start: time                    # UTC time when session opens
    utc_end: time                      # UTC time when session closes
    is_open: bool = False
    volatility_index: float = 50       # 0-100 scale
    avg_spread: float = 2              # Average pip spread
    session_high: float = 0
    session_low: float = 0


@dataclass
class MarketConditions:
    """Current market conditions."""
    timestamp: datetime
    sessions_open: List[MarketSession]
    overall_volatility: float         # 0-100
    avg_spread: float
    trending: TrendDirection
    trend_strength: float             # 0-100
    session_states: Dict[MarketSession, SessionState]


class MarketMonitor:
    """Monitors market sessions and conditions."""
    
    # Session times (UTC)
    SESSION_TIMES = {
        MarketSession.TOKYO: (time(20, 0), time(9, 0)),      # Sunday 20:00 to Friday 09:00
        MarketSession.LONDON: (time(8, 0), time(17, 0)),     # 08:00-17:00 UTC
        MarketSession.NEW_YORK: (time(13, 0), time(22, 0)),  # 13:00-22:00 UTC
        MarketSession.SYDNEY: (time(21, 0), time(6, 0)),     # 21:00-06:00 UTC
    }
    
    # Session overlaps (when volatility increases)
    # More active = higher spreads and volatility
    SESSION_ACTIVITY = {
        MarketSession.TOKYO: 40,        # Base activity
        MarketSession.LONDON: 80,       # Most active
        MarketSession.NEW_YORK: 90,     # Very active
        MarketSession.SYDNEY: 30,       # Slow session
    }
    
    # Pair-specific spreads (in pips)
    PAIR_SPREADS = {
        "EURUSD": 2,
        "GBPUSD": 2,
        "USDJPY": 2,
        "AUDUSD": 2,
        "NZDUSD": 3,
        "USDCAD": 2,
        "USDCHF": 2,
    }
    
    def __init__(self):
        """Initialize market monitor."""
        self.session_states: Dict[MarketSession, SessionState] = {}
        self._initialize_sessions()
        
        self.market_history: List[MarketConditions] = []
        self.current_conditions: Optional[MarketConditions] = None

    def _initialize_sessions(self) -> None:
        """Initialize session states."""
        for session, (start, end) in self.SESSION_TIMES.items():
            self.session_states[session] = SessionState(
                session=session,
                utc_start=start,
                utc_end=end,
            )

    def update_market_conditions(
        self,
        pair: str,
        current_price: float,
        price_history: List[float],
        current_volatility: Optional[float] = None,
    ) -> MarketConditions:
        """
        Update market conditions based on price and session data.
        
        Args:
            pair: Currency pair
            current_price: Current market price
            price_history: Recent price history for volatility calculation
            current_volatility: Optional volatility override (0-100)
            
        Returns:
            Updated MarketConditions
        """
        now = datetime.utcnow()
        
        # Update session states
        self._update_sessions(now)
        
        # Calculate market volatility
        if current_volatility is None:
            volatility = self._calculate_volatility(price_history)
        else:
            volatility = current_volatility
        
        # Adjust volatility based on session overlap
        active_sessions = self._get_active_sessions()
        session_activity = sum(
            self.SESSION_ACTIVITY.get(s, 50) for s in active_sessions
        ) / max(len(active_sessions), 1)
        
        volatility = volatility * (session_activity / 50)  # Adjust by activity
        volatility = min(max(volatility, 0), 100)  # Clamp to 0-100
        
        # Get average spread
        avg_spread = self.PAIR_SPREADS.get(pair, 2)
        
        # Adjust spread based on volatility and session
        if len(active_sessions) > 1:  # Session overlap
            avg_spread *= 1.5
        avg_spread += (volatility / 50)  # Add volatility component
        
        # Determine trend
        trend_dir, trend_str = self._calculate_trend(price_history)
        
        conditions = MarketConditions(
            timestamp=now,
            sessions_open=active_sessions,
            overall_volatility=volatility,
            avg_spread=avg_spread,
            trending=trend_dir,
            trend_strength=trend_str,
            session_states=self.session_states,
        )
        
        self.current_conditions = conditions
        self.market_history.append(conditions)
        
        return conditions

    def _update_sessions(self, now: datetime) -> None:
        """Update whether each session is currently open."""
        utc_now = now.time()
        day_of_week = now.weekday()  # 0=Monday, 4=Friday
        
        for session, state in self.session_states.items():
            is_open = False
            
            # Tokyo: Sunday 20:00 to Friday 09:00 (crosses midnight)
            if session == MarketSession.TOKYO:
                is_open = (
                    (day_of_week < 5 and utc_now >= state.utc_start) or
                    (day_of_week < 5 and utc_now < state.utc_end)
                )
            
            # London: 08:00-17:00
            elif session == MarketSession.LONDON:
                is_open = state.utc_start <= utc_now < state.utc_end and day_of_week < 5
            
            # New York: 13:00-22:00
            elif session == MarketSession.NEW_YORK:
                is_open = state.utc_start <= utc_now < state.utc_end and day_of_week < 5
            
            # Sydney: 21:00-06:00 (crosses midnight)
            elif session == MarketSession.SYDNEY:
                is_open = (
                    (utc_now >= state.utc_start) or (utc_now < state.utc_end)
                )
            
            state.is_open = is_open

    def _get_active_sessions(self) -> List[MarketSession]:
        """Get currently active trading sessions."""
        return [s for s, state in self.session_states.items() if state.is_open]

    def _calculate_volatility(self, price_history: List[float]) -> float:
        """
        Calculate volatility as a 0-100 score.
        
        Args:
            price_history: Recent price history
            
        Returns:
            Volatility score 0-100
        """
        if len(price_history) < 2:
            return 50  # Default
        
        # Calculate percent changes
        changes = []
        for i in range(1, len(price_history)):
            change = abs((price_history[i] - price_history[i-1]) / price_history[i-1]) * 100
            changes.append(change)
        
        # Average change as volatility
        avg_change = sum(changes) / len(changes) if changes else 0
        
        # Scale to 0-100 (assume 0.2% = very low, 2% = very high)
        volatility = min(avg_change * 50, 100)
        
        return volatility

    def _calculate_trend(
        self,
        price_history: List[float],
    ) -> Tuple[TrendDirection, float]:
        """
        Calculate trend direction and strength.
        
        Args:
            price_history: Recent price history
            
        Returns:
            (trend_direction, trend_strength 0-100)
        """
        if len(price_history) < 5:
            return TrendDirection.SIDEWAYS, 0
        
        # Simple trend: compare first 5 to last 5
        early_avg = sum(price_history[:5]) / 5
        late_avg = sum(price_history[-5:]) / 5
        
        if late_avg > early_avg * 1.001:
            direction = TrendDirection.BULLISH
            strength = min(((late_avg - early_avg) / early_avg) * 10000, 100)
        elif late_avg < early_avg * 0.999:
            direction = TrendDirection.BEARISH
            strength = min(((early_avg - late_avg) / early_avg) * 10000, 100)
        else:
            direction = TrendDirection.SIDEWAYS
            strength = 0
        
        return direction, strength

    def check_invalidation_signals(
        self,
        position_direction: str,
        entry_price: float,
        current_price: float,
        conviction_level: str,
        stop_loss: float,
    ) -> Optional[str]:
        """
        Check if position should be invalidated due to market conditions.
        
        Args:
            position_direction: LONG or SHORT
            entry_price: Entry price
            current_price: Current price
            conviction_level: From Phase 3 (%).
            stop_loss: Stop loss price
            
        Returns:
            Invalidation reason or None if trade is still valid
        """
        if not self.current_conditions:
            return None
        
        conditions = self.current_conditions
        
        # High volatility spike: consider closing low-conviction trades
        if conditions.overall_volatility > 80:
            if conviction_level and int(conviction_level.rstrip('%')) < 60:
                return "High volatility + low conviction"
        
        # Trend reversal: check if opposite trend is strong
        if position_direction == "LONG" and conditions.trending == TrendDirection.BEARISH:
            if conditions.trend_strength > 70:
                return "Strong bearish trend reversal"
        elif position_direction == "SHORT" and conditions.trending == TrendDirection.BULLISH:
            if conditions.trend_strength > 70:
                return "Strong bullish trend reversal"
        
        # Session change: closing sessions may have slippage
        if len(conditions.sessions_open) < 2:
            # Check if we're between sessions (low liquidity)
            pass  # Could trigger closure of marginal trade
        
        # Extreme spread: may indicate fast market
        if conditions.avg_spread > 5:
            if current_price > entry_price:
                # In a winning position; maybe take profit early
                pass
            else:
                # In a losing position; consider cutting loss
                return "Extreme spread (low liquidity)"
        
        return None

    def get_session_quality(self) -> Dict[str, str]:
        """Get quality assessment of each session."""
        assessments = {}
        for session, state in self.session_states.items():
            if state.is_open:
                activity = self.SESSION_ACTIVITY.get(session, 50)
                if activity > 80:
                    quality = "Very Active"
                elif activity > 60:
                    quality = "Active"
                else:
                    quality = "Quiet"
                assessments[session.value] = quality
        
        return assessments

    def get_best_trading_session(self) -> Optional[str]:
        """Get most active current session (best for trading)."""
        active = [(s, self.SESSION_ACTIVITY.get(s, 50)) for s in self._get_active_sessions()]
        if not active:
            return None
        
        best = max(active, key=lambda x: x[1])
        return best[0].value

    def get_market_summary(self) -> Dict[str, any]:
        """Get current market summary."""
        if not self.current_conditions:
            return {}
        
        cond = self.current_conditions
        return {
            'timestamp': cond.timestamp.isoformat(),
            'active_sessions': [s.value for s in cond.sessions_open],
            'volatility_score': round(cond.overall_volatility, 1),
            'average_spread': round(cond.avg_spread, 1),
            'trend': cond.trending.value,
            'trend_strength': round(cond.trend_strength, 1),
            'market_quality': self.get_session_quality(),
            'best_session': self.get_best_trading_session(),
        }

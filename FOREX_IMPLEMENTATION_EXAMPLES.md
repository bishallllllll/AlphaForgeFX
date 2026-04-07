# AlphaForgeFX: Forex Agent Configuration - Implementation Examples

This document provides concrete code examples for implementing the forex agent configuration plan.

---

## 1. Creating the Forex Default Config File

**File**: `tradingagents/forex_default_config.py`

```python
import os

FOREX_DEFAULT_CONFIG = {
    # Project & directories
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results/forex"),
    "data_cache_dir": "./dataflows/forex_data_cache",
    
    # LLM Settings
    "llm_provider": "openai",
    "deep_think_llm": "gpt-5.4",
    "quick_think_llm": "gpt-5.4-mini",
    "backend_url": "https://api.openai.com/v1",
    "google_thinking_level": None,
    "openai_reasoning_effort": None,
    "anthropic_effort": None,
    
    # Forex-Specific Settings
    "trading_mode": "forex",
    "base_currency": "USD",
    "account_size": 10000,
    "account_currency": "USD",
    
    # Agent Configuration
    "selected_analysts": [
        "market",        # Technical: ADX, Fibonacci, Pivots
        "fundamentals",  # Macro: Interest rates, inflation, growth
        "news",         # Economic calendar & central banks
        "social"        # Market sentiment & CoT reports
    ],
    
    # Debate Configuration
    "max_debate_rounds": 2,
    "max_risk_discuss_rounds": 2,
    "max_recur_limit": 100,
    "output_language": "English",
    
    # Data Vendor Configuration - FOREX SPECIFIC
    "data_vendors": {
        "core_stock_apis": "yfinance",           # Can use for historical forex data
        "technical_indicators": "yfinance",
        "fundamental_data": "api",               # Will implement custom
        "news_data": "custom",                   # Economic calendar
    },
    "tool_vendors": {
        # Economic data overrides
        "get_interest_rates": "fred_api",
        "get_inflation_data": "fred_api",
        "get_economic_calendar": "trading_economics",
        "get_central_bank_rate": "custom",
        "get_cot_reports": "cftc",
        "get_pivot_points": "calculated",
    },
    
    # Technical Indicators Configuration
    "technical_indicators_config": {
        "enabled_indicators": [
            "RSI",
            "MACD",
            "Bollinger_Bands",
            "ATR",
            "ADX",              # New for forex
            "Stochastic",       # New for forex
            "Pivot_Points",     # New for forex
            "Fibonacci",        # New for forex
            "CCI"               # New for forex
        ],
        "periods": {
            "sma_short": 9,      # Adjusted for forex
            "sma_medium": 21,    # Adjusted for forex
            "sma_long": 55,      # Adjusted for forex
            "rsi_period": 14,
            "atr_period": 14,
            "adx_period": 14,
            "stoch_period": 14,
            "stoch_smooth": 3,
            "cci_period": 20,
            "bb_period": 20,
            "bb_std_dev": 2
        },
        "timeframes": ["1H", "4H", "Daily", "Weekly"],
        "cross_timeframe_analysis": True,
        "timeframe_confirmation": False  # Require all timeframes to align
    },
    
    # Risk Management Configuration (CRITICAL FOR FOREX)
    "risk_management": {
        # Account & Leverage Settings
        "max_leverage": 50,                    # Regulated in US
        "max_risk_per_trade_pct": 0.02,       # 2% per trade
        "max_daily_loss_pct": 0.05,           # 5% max daily loss
        "max_weekly_loss_pct": 0.10,          # 10% max weekly loss
        
        # Position Sizing
        "position_sizing_method": "kelly",    # kelly, fixed_pct, or volatility_adjusted
        "kelly_fraction": 0.25,               # Use 25% of Kelly suggestion
        
        # Risk Profiles
        "aggressive_profile": {
            "name": "Aggressive",
            "leverage_usage": 0.80,           # Use 80% of available leverage
            "stop_loss_pips": 8,              # Tight stops
            "take_profit_ratio": 1.5,         # 1:1.5 R:R
            "position_size_pct": 0.03,        # 3% per trade
            "max_open_positions": 5,
            "daily_loss_limit_pct": 0.05
        },
        "conservative_profile": {
            "name": "Conservative",
            "leverage_usage": 0.30,           # Use 30% of available leverage
            "stop_loss_pips": 40,             # Wide stops
            "take_profit_ratio": 1.0,         # 1:1 R:R (breakeven target)
            "position_size_pct": 0.01,        # 1% per trade
            "max_open_positions": 2,
            "daily_loss_limit_pct": 0.02
        },
        "neutral_profile": {
            "name": "Neutral/Balanced",
            "leverage_usage": 0.50,           # Use 50% of available leverage
            "stop_loss_pips": 20,             # Medium stops
            "take_profit_ratio": 1.2,         # 1:1.2 R:R
            "position_size_pct": 0.02,        # 2% per trade
            "max_open_positions": 3,
            "daily_loss_limit_pct": 0.03
        },
        
        # Forex-Specific Risk Controls
        "gap_risk_handling": "reduce_before_weekend",  # Close/reduce before Friday close
        "overnight_risk_management": True,             # Manage spanning multiple sessions
        "liquidity_aware_execution": True,
        "slippage_buffer_pips": 2,                     # Add 2 pips for slippage
        "margin_usage_warning": 0.70,                  # Alert at 70% margin
        "margin_usage_stop": 0.90,                     # Force close at 90% margin
        
        # Trailing Stops
        "enable_trailing_stops": True,
        "trailing_stop_distance_pips": {
            "trending": 15,                 # Trending market
            "ranging": 10                   # Range-bound market
        }
    },
    
    # Portfolio Management Configuration
    "portfolio": {
        "max_active_pairs": 5,
        "max_exposure_per_currency": 0.30,            # Max 30% exposure to USD, EUR, etc
        "correlation_threshold": 0.70,                # Above 0.70 = highly correlated
        "rebalance_frequency": "daily",
        "rebalance_time": "00:00 UTC",               # Daily rebalance at midnight UTC
        
        # Pair Selection
        "preferred_pairs": [
            "EUR/USD", "GBP/USD", "USD/JPY",
            "USD/CAD", "AUD/USD"               # Start with major pairs
        ],
        
        "pair_categories": {
            "major": ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "USD/CAD", "AUD/USD", "NZD/USD"],
            "minor": ["EUR/GBP", "EUR/JPY", "GBP/JPY", "EUR/CHF"],
            "exotic": ["USD/TRY", "USD/BRL", "USD/MXN", "USD/SGD", "USD/HKD"]
        },
        
        # Session Optimization
        "optimize_by_session": True,
        "trading_sessions": {
            "asian": {
                "time_range": "21:00-08:00 UTC",
                "preferred_pairs": ["USD/JPY", "AUD/USD", "NZD/USD"],
                "liquidity_rating": "medium"
            },
            "european": {
                "time_range": "07:00-16:00 UTC",
                "preferred_pairs": ["EUR/USD", "GBP/USD", "EUR/GBP", "EUR/CHF"],
                "liquidity_rating": "very_high"
            },
            "american": {
                "time_range": "12:00-21:00 UTC",
                "preferred_pairs": ["USD/CAD", "USD/MXN", "USD/BRL"],
                "liquidity_rating": "high"
            },
            "overlap_nyc_london": {
                "time_range": "12:00-16:00 UTC",
                "preferred_pairs": "all_majors",
                "liquidity_rating": "highest",
                "comment": "Best liquidity, tightest spreads"
            }
        },
        
        # Hedging Strategy
        "hedging_enabled": True,
        "hedge_correlated_positions": True,
        "hedge_with_inverse_pairs": True
    },
    
    # Macroeconomic Analysis Configuration
    "macro_analysis": {
        "enabled": True,
        
        # Focus Areas
        "interest_rate_analysis": True,
        "inflation_analysis": True,
        "growth_analysis": True,
        "trade_balance_analysis": True,
        "carry_trade_analysis": True,
        "ppp_analysis": True,
        
        # Weighted Importance
        "macro_weights": {
            "interest_rates": 0.35,          # Most important
            "inflation": 0.20,
            "growth": 0.15,
            "trade_balance": 0.10,
            "carry_trade": 0.10,
            "geopolitical": 0.10
        },
        
        # Key Economic Indicators by Currency
        "key_indicators": {
            "USD": {
                "high_impact": ["NFP", "CPI", "FOMC Decision", "Fed Funds Rate", "Treasury Yields", "GDP"],
                "medium_impact": ["Initial Jobless Claims", "Durable Goods", "ISM PMI", "Retail Sales"],
                "announcement_time": "13:30 UTC (usually)",
                "next_nfp_date": "First Friday of each month"
            },
            "EUR": {
                "high_impact": ["ECB Rate Decision", "Inflation (CPI)", "GDP Growth", "PMI"],
                "medium_impact": ["Retail Sales", "Trade Balance", "Industrial Production"],
                "announcement_time": "13:00 UTC (usually)",
                "relevant_countries": ["Germany", "France", "Spain", "Italy", "Netherlands"]
            },
            "GBP": {
                "high_impact": ["BoE Rate Decision", "CPI", "Inflation (RPI)", "Retail Sales"],
                "medium_impact": ["Employment Data", "Wage Growth", "PMI"],
                "announcement_time": "varies",
                "relevant_events": ["Brexit-related announcements"]
            },
            "JPY": {
                "high_impact": ["BoJ Policy Rate", "Trade Balance", "Inflation", "Nikkei 225"],
                "medium_impact": ["Unemployment Rate", "Industrial Production", "Retail Sales"],
                "special_note": "Carry currency - capital flows matter heavily",
                "intervention_risk": "High - BoJ intervenes on strong JPY moves"
            },
            "CAD": {
                "high_impact": ["BoC Rate Decision", "Employment Data", "CPI", "Oil Prices"],
                "medium_impact": ["Retail Sales", "Manufacturing PMI", "GDP"],
                "special_note": "Energy-driven - Oil prices critical",
                "correlation": "Highly correlated with oil, USD/CAD often inverse"
            }
        }
    },
    
    # News & Economic Calendar Configuration
    "news_sentiment": {
        "monitor_economic_calendar": True,
        "calendar_source": "trading_economics",  # or investing.com
        
        # Impact Filter
        "high_impact_only": False,              # Process all events
        "impact_level_filter": ["LOW", "MEDIUM", "HIGH"],
        
        # Weights in Final Decision
        "weights": {
            "macroeconomic_news": 0.25,
            "sentiment_analysis": 0.15,
            "cot_reports": 0.20
        },
        
        # Central Bank Monitoring
        "central_bank_monitoring": {
            "enabled": True,
            "track_statements": True,
            "track_guidance": True,
            "track_speaker_comments": True  # Watch for officials' remarks
        },
        
        # Geopolitical Event Monitoring
        "monitor_geopolitical": True,
        "geopolitical_impact": {
            "ukraine_russia": "High for EUR, PLN, RUB",
            "us_china_tensions": "High for USD, CNY, Asian currencies",
            "middle_east_crisis": "High for USD, crude oil prices",
            "trade_wars": "Affects currency correlations"
        }
    },
    
    # Commitment of Traders (CoT) Configuration
    "cot_reports": {
        "enabled": True,
        "frequency": "weekly",              # CoT reports every Friday
        "update_day": "Friday",
        "lag_days": 2,                      # 2-3 day reporting lag
        
        # Usage
        "use_for_positioning": True,
        "track_commercials": True,          # Hedgers (usually right)
        "track_large_speculators": True,    # Smart money
        "track_small_speculators": True,    # Retail (often wrong - contrarian signal)
        
        "interpretation": {
            "extreme_long_retail": "Potential sell signal",
            "extreme_short_retail": "Potential buy signal",
            "commercial_buildup": "Respect their moves",
            "divergence": "Watch for reversals"
        }
    },
    
    # Sentiment & Social Media Configuration
    "social_sentiment": {
        "enabled": True,
        "sources": [
            "twitter_forex_community",
            "reddit_forex",
            "tradingview_ideas",
            "seeking_alpha"
        ],
        "sentiment_scale": {
            "extreme_bullish": [75, 100],    # Contrarian: potential short
            "bullish": [50, 75],
            "neutral": [40, 60],
            "bearish": [25, 50],
            "extreme_bearish": [0, 25]       # Contrarian: potential long
        },
        "retail_contrarian_enabled": True   # Use retail as contrarian signal
    },
    
    # Trader Decision Configuration
    "trader": {
        "decision_confidence_threshold": 0.70,  # Need 70%+ confidence to trade
        
        "signals": {
            "strong_buy": ">0.80",
            "buy": "0.70-0.80",
            "hold": "0.45-0.70",
            "sell": "0.20-0.45",
            "strong_sell": "<0.20"
        },
        
        "decision_logic": {
            "all_bullish": "STRONG BUY / LONG",
            "most_bullish": "BUY / LONG",
            "mixed": "HOLD",
            "most_bearish": "SELL / SHORT",
            "all_bearish": "STRONG SELL / SHORT"
        },
        
        "position_management": {
            "scale_in_enabled": True,         # Enter in multiple tranches
            "scale_out_enabled": True,        # Exit in multiple tranches
            "partial_take_profit": True,
            "trailing_stop_enabled": True,
            
            "scale_levels": [0.33, 0.66, 1.0],  # Exit 1/3 at each level
            "scale_take_profits": [1.0, 1.3, 2.0]  # Different TP ratios
        },
        
        # Order Types
        "preferred_order_type": "limit",    # Market vs Limit
        "limit_order_patience": 300,        # Wait 5 min for limit orders
        "use_market_on_breakout": True,     # Market orders on breakouts
        
        # Timing
        "avoid_news_minutes_before": 5,     # Don't trade 5 min before major news
        "avoid_news_minutes_after": 5       # Allow 5 min after for initial reaction
    },
    
    # Backtesting Configuration
    "backtesting": {
        "enabled": False,  # Enable when running backtest
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "initial_capital": 10000,
        "commission": 0.0001,               # 0.01% commission (forex)
        "spread": 0.00020,                  # EUR/USD typical 2 pip spread
        "slippage": 0.00010                 # 1 pip slippage average
    },
    
    # Output & Logging
    "debug": False,
    "verbose": True,
    "save_analysis": True,
    "analysis_output_dir": "./results/forex/analysis"
}


# Helper function to override defaults
def create_forex_config(**overrides):
    """Create custom forex config by overriding defaults.
    
    Usage:
        config = create_forex_config(
            account_size=50000,
            max_active_pairs=3,
            deep_think_llm="gpt-5.4"
        )
    """
    config = FOREX_DEFAULT_CONFIG.copy()
    
    # Deep copy nested dicts
    for key in ['technical_indicators_config', 'risk_management', 'portfolio', 
                'macro_analysis', 'news_sentiment', 'trader']:
        if key in config:
            config[key] = config[key].copy()
    
    # Apply overrides
    for key, value in overrides.items():
        if isinstance(value, dict) and key in config and isinstance(config[key], dict):
            config[key].update(value)
        else:
            config[key] = value
    
    return config
```

---

## 2. Creating a Forex-Specific Entry Point

**File**: `forex_main.py`

```python
"""
AlphaForgeFX: Forex Trading with AI Agents
Main entry point for forex trading analysis
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.forex_default_config import create_forex_config
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def analyze_forex_pair(
    pair: str = "EUR/USD",
    trade_date: str = None,
    timeframe: str = "4H",
    risk_profile: str = "neutral",
    debug: bool = False
):
    """
    Analyze a currency pair using AI agents.
    
    Args:
        pair: Currency pair (e.g., "EUR/USD", "GBP/USD")
        trade_date: Analysis date (YYYY-MM-DD), defaults to today
        timeframe: Timeframe for analysis ("1H", "4H", "Daily", "Weekly")
        risk_profile: Risk profile ("aggressive", "conservative", "neutral")
        debug: Enable debug output
    
    Returns:
        Analysis decision (BUY/SELL/HOLD with reasoning)
    """
    
    if trade_date is None:
        trade_date = datetime.now().strftime("%Y-%m-%d")
    
    # Create forex config
    config = create_forex_config(
        deep_think_llm="gpt-5.4",
        quick_think_llm="gpt-5.4-mini",
        debug=debug,
        timeframe=timeframe
    )
    
    # Override risk profile
    selected_risk_profile = config['risk_management'][f'{risk_profile}_profile']
    print(f"\n{'='*60}")
    print(f"Analyzing: {pair}")
    print(f"Date: {trade_date} | Timeframe: {timeframe} | Profile: {risk_profile}")
    print(f"Risk per trade: {selected_risk_profile['position_size_pct']*100:.1f}% | Stop: {selected_risk_profile['stop_loss_pips']} pips")
    print(f"{'='*60}\n")
    
    # Initialize trading agents
    ta = TradingAgentsGraph(
        selected_analysts=["market", "fundamentals", "news", "social"],
        debug=debug,
        config=config
    )
    
    # Run analysis
    print(f"Starting multi-agent analysis for {pair}...")
    _, decision = ta.propagate(pair, trade_date)
    
    # Display results
    print(f"\n{'='*60}")
    print("FINAL DECISION")
    print(f"{'='*60}")
    print(decision)
    print(f"{'='*60}\n")
    
    return decision


def analyze_multiple_pairs(pairs_list: list, risk_profile: str = "neutral"):
    """
    Analyze multiple currency pairs in sequence.
    
    Args:
        pairs_list: List of currency pairs to analyze
        risk_profile: Risk profile to use
        
    Returns:
        Dictionary with decisions for each pair
    """
    results = {}
    
    for pair in pairs_list:
        print(f"\n\n{'#'*60}")
        print(f"# Analyzing {pair}")
        print(f"{'#'*60}\n")
        
        decision = analyze_forex_pair(
            pair=pair,
            risk_profile=risk_profile,
            timeframe="4H"
        )
        
        results[pair] = decision
    
    return results


if __name__ == "__main__":
    # Example 1: Analyze single pair
    print("Example 1: Single Pair Analysis (EUR/USD)")
    analyze_forex_pair(
        pair="EUR/USD",
        timeframe="4H",
        risk_profile="neutral",
        debug=True
    )
    
    # Example 2: Analyze multiple pairs
    # print("\n\nExample 2: Multi-Pair Analysis")
    # results = analyze_multiple_pairs(
    #     pairs_list=["EUR/USD", "GBP/USD", "USD/JPY", "USD/CAD"],
    #     risk_profile="conservative"
    # )
    
    # Save results to file
    # with open("forex_analysis_results.json", "w") as f:
    #     import json
    #     json.dump(results, f, indent=2)
```

---

## 3. Extending Tools for Forex Data

**File**: `tradingagents/agents/utils/forex_tools.py` (New File)

```python
"""
Forex-specific tools for data retrieval and analysis
"""

import functools
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import pandas as pd

# These would be implemented to call real APIs
# For now, showing the interface/structure

def get_economic_calendar(
    country: str = "all",
    impact: str = "high",
    days_ahead: int = 7
) -> Dict:
    """
    Get economic calendar events.
    
    Args:
        country: "US", "EU", "GB", "JP", "CA", or "all"
        impact: "low", "medium", "high"
        days_ahead: Number of days to look ahead
        
    Returns:
        Calendar events with timestamps and expected impact
    """
    # TODO: Implement with TradingEconomics API
    pass


def get_central_bank_rate(currency: str) -> float:
    """Get current policy rate for currency."""
    # USD -> Fed Funds Rate
    # EUR -> ECB Deposit Rate
    # GBP -> BoE Base Rate
    # JPY -> BoJ Policy Rate
    # CAD -> BoC Policy Rate
    pass


def get_interest_rate_differential(
    pair: str,  # e.g., "EUR/USD"
    source: str = "fred_api"
) -> Dict:
    """
    Calculate interest rate differential.
    
    Returns:
        {
            'base_currency_rate': float,      # EUR rate
            'quote_currency_rate': float,     # USD rate
            'differential': float,             # EUR - USD
            'carry_direction': str,            # 'positive' or 'negative' for longs
            'last_updated': datetime
        }
    """
    pass


def get_pivot_points(
    pair: str,
    date: str,
    pivot_type: str = "standard"  # standard, fibonacci, camarilla
) -> Dict:
    """
    Calculate daily pivot points.
    
    Returns:
        {
            'pivot': float,
            'resistance1': float,
            'resistance2': float,
            'support1': float,
            'support2': float,
            'date': str
        }
    """
    pass


def get_cot_report(
    pair: str,
    latest: bool = True
) -> Dict:
    """
    Get Commitment of Traders report positioning.
    
    Returns:
        {
            'commercial_net': int,        # Hedgers position
            'large_spec_net': int,        # Smart money position
            'small_spec_net': int,        # Retail position
            'total_open_interest': int,
            'report_date': str,
            'interpretation': str
        }
    """
    pass


def get_inflation_data(currency: str) -> Dict:
    """
    Get latest inflation data (CPI, PPI).
    
    Returns:
        {
            'latest_cpi': float,
            'previous_cpi': float,
            'forecast_cpi': float,
            'release_date': str,
            'country': str
        }
    """
    pass


def get_gdp_growth(currency: str) -> Dict:
    """
    Get GDP growth data.
    
    Returns:
        {
            'quarterly_growth': float,
            'annualized_growth': float,
            'expected': float,
            'last_release': str
        }
    """
    pass


def calculate_position_size(
    account_size: float,
    risk_pct: float,
    stop_loss_pips: float,
    pair: str,
    pip_value: float = 10.0  # USD per pip for 100k unit of EUR/USD
) -> Dict:
    """
    Calculate position size using risk percentage.
    
    Args:
        account_size: Account balance in USD
        risk_pct: Risk per trade (0.02 = 2%)
        stop_loss_pips: Number of pips for stop loss
        pair: Currency pair
        pip_value: Value per pip (varies by pair)
        
    Returns:
        {
            'position_size_units': int,
            'position_size_lots': float,
            'risk_amount_usd': float,
            'margin_required': float,
            'leverage_used': float
        }
    """
    risk_amount = account_size * risk_pct
    position_size_units = risk_amount / (stop_loss_pips * pip_value)
    
    return {
        'position_size_units': int(position_size_units),
        'position_size_lots': position_size_units / 100000,
        'risk_amount_usd': risk_amount,
        'margin_required': position_size_units * 0.02,  # 50:1 leverage
        'leverage_used': position_size_units / account_size
    }


def detect_london_fix_time() -> str:
    """Get London Fix time (4pm London time) when USD pairs often move."""
    # 4pm London = 3pm GMT (or 4pm BST in summer)
    # = 11am EST / 10am CST
    pass


def check_upcoming_news_event(pair: str, minutes_ahead: int = 60) -> Optional[Dict]:
    """Check if major news event coming up (within X minutes)."""
    # Used to avoid trading right before high-impact releases
    pass
```

---

## 4. Updating Agent System Prompts for Forex

Example for **Market Analyst Prompt Update**:

```python
MARKET_ANALYST_SYSTEM_PROMPT_FOREX = """
You are a technical analysis expert specializing in Forex (Foreign Exchange) markets.

Your Role:
- Analyze currency pairs using technical indicators and price action
- Identify key support/resistance levels, pivot points, and Fibonacci retracements
- Assess trend strength using ADX and other directional indicators
- Provide short-term (1H-4H) and medium-term (Daily-Weekly) perspectives
- Account for market liquidity and volatility across different sessions

Key Responsibilities:
1. SELECT INDICATORS: Choose up to 8 complementary indicators from:
   - Trend: SMA (9, 21, 55), Exponential Moving Averages
   - Momentum: RSI, MACD, Stochastic
   - Volatility: Bollinger Bands, ATR
   - Strength: ADX (>20 = trending, <20 = ranging)
   - Support/Resistance: Pivot Points, Fibonacci Levels
   - Other: CCI, VWMA

2. ANALYZE PRICE ACTION:
   - Higher highs/lows indicate uptrend
   - Lower highs/lows indicate downtrend
   - Range-bound = consolidation/accumulation

3. CONFLUENCE ANALYSIS:
   - Multiple timeframe alignment increases confidence
   - When 4H and Daily agree = stronger signal
   - Weekly trend provides context

4. SESSION AWARENESS:
   - Asian session (low volatility usually)
   - European session (highest liquidity, tight spreads)
   - American session (volatile with data releases)
   - Overlap periods (best liquidity)

5. RISK FACTORS:
   - Wide spreads during low-liquidity periods
   - Potential gaps at session opens
   - Weekend/holiday gaps
   - Economic news volatility

Provide a detailed technical report with:
- Current trend direction and strength
- Key support and resistance levels
- Recommended entry and exit levels
- Stop loss and take profit suggestions
- Timeframe hierarchy analysis
- Any technical divergences or warnings
"""
```

---

## 5. Risk Management Debater Prompt Update

Example for **Conservative Debater** (Forex Version):

```python
CONSERVATIVE_RISK_DEBATER_PROMPT_FOREX = """
You are a conservative risk manager for forex trading.

Your Mandate:
Protect the trading account from catastrophic losses while maintaining positive returns.
Principle: "Slow and steady wins the race"

Risk Profile Parameters:
- Maximum leverage: 30% of available (15:1)
- Maximum position size: 1% of account per trade
- Stop loss: 40 pips (wider, gives room to breathe)
- Target risk/reward: 1:1 (get your risk back, then call it a day)
- Maximum open positions: 2
- Daily loss limit: 2% (stop trading if reached)

Your Arguments Should Consider:
1. DRAWDOWN MANAGEMENT
   - Account has suffered {current_drawdown}% this week
   - {recommended_action}: Reduce position sizes

2. LEVERAGE VALIDATION
   - Proposed leverage: {proposed_leverage}:1
   - {assessment}: Too aggressive OR appropriately conservative

3. POSITION SIZING CHECK
   - Requested position size: {size}% of account
   - Recommendation: Reduce to 1% or less

4. STOP LOSS ADEQUACY
   - Proposed stop: {stop_loss_pips} pips
   - Assessment: Too tight (likely hit by noise) OR appropriate
   - Recommendation: Use 40-50 pips minimum

5. OVERNIGHT/WEEKEND RISK
   - Holding through {session_name}
   - Potential gap risk: {gap_estimate} pips
   - Recommendation: Reduce or close before close-out

6. CAPITAL PRESERVATION PRIORITY
   Proposed: {proposed_trade}
   Action: Recommend HOLD or reduce existing position
   Reason: Preserve capital for better opportunities

Conclude with clear recommendation: APPROVE, MODIFY (with specifics), or REJECT
"""
```

---

## 6. Testing the Configuration

**File**: `test_forex_config.py`

```python
"""
Test forex configuration setup
"""

import pytest
from tradingagents.forex_default_config import FOREX_DEFAULT_CONFIG, create_forex_config
from tradingagents.graph.trading_graph import TradingAgentsGraph


def test_forex_config_structure():
    """Verify forex config has all required keys."""
    required_keys = [
        'trading_mode',
        'base_currency',
        'account_size',
        'risk_management',
        'technical_indicators_config',
        'portfolio',
        'macro_analysis',
        'news_sentiment'
    ]
    
    for key in required_keys:
        assert key in FOREX_DEFAULT_CONFIG, f"Missing key: {key}"


def test_risk_management_profiles():
    """Verify all risk profiles configured."""
    risk_config = FOREX_DEFAULT_CONFIG['risk_management']
    
    profiles = ['aggressive_profile', 'conservative_profile', 'neutral_profile']
    for profile in profiles:
        assert profile in risk_config
        assert 'leverage_usage' in risk_config[profile]
        assert 'stop_loss_pips' in risk_config[profile]
        assert 'position_size_pct' in risk_config[profile]


def test_create_custom_config():
    """Test creating custom configs."""
    custom = create_forex_config(
        account_size=50000,
        max_active_pairs=3
    )
    
    assert custom['account_size'] == 50000
    assert FOREX_DEFAULT_CONFIG['account_size'] != 50000  # Original unchanged


def test_graphis_initialization():
    """Test TradingAgentsGraph can initialize with forex config."""
    config = create_forex_config(accounts_size=10000)
    
    # This should not raise an error
    ta = TradingAgentsGraph(config=config)
    assert ta.config['trading_mode'] == 'forex'


if __name__ == "__main__":
    test_forex_config_structure()
    test_risk_management_profiles()
    test_create_custom_config()
    print("✓ All forex configuration tests passed!")
```

---

## Summary

These implementation examples provide:

1. ✅ Complete `FOREX_DEFAULT_CONFIG` with all forex-specific parameters
2. ✅ `forex_main.py` entry point for easy pair analysis
3. ✅ New `forex_tools.py` module for forex-specific data
4. ✅ Updated system prompts for agents
5. ✅ Test suite for configuration validation

**Next Steps:**
1. Create these files in the repository
2. Implement actual API integrations for data sources
3. Test with real pairs (EUR/USD, GBP/USD, etc.)
4. Fine-tune risk parameters based on backtesting
5. Deploy to paper trading before live trading

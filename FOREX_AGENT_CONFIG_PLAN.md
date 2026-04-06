# AlphaForgeFX: Agent Configuration Plan for Forex Trading

## Executive Summary
This document outlines the configuration strategy to adapt the TradingAgents framework from equities trading to **Forex (Foreign Exchange) Trading**. Forex presents unique challenges and opportunities compared to stock trading, requiring significant modifications to agent behavior, data sources, tools, and risk management strategies.

---

## Part 1: Key Differences - Forex vs. Equities Trading

| Aspect | Equities | Forex |
|--------|----------|-------|
| **Trading Hours** | Market-specific (NYSE: 9:30-16:00 EST) | 24/5 (Sun 5pm-Fri 5pm EST) |
| **Liquidity** | High but varies by stock | Ultra-high in major pairs (EUR/USD, GBP/USD) |
| **Volatility** | Company/sector dependent | Driven by macroeconomic events, central banks |
| **Leverage** | Typically 1:1 or 2:1 | Common 50:1 - 500:1 (highly regulated) |
| **Instruments** | Individual stocks, ETFs | Currency pairs (majors, minors, exotics) |
| **Key Drivers** | Earnings, company news, sector trends | Interest rates, GDP, employment, geopolitical events |
| **Time Frames** | Minutes to years | Minutes to weeks (scalpers to position traders) |
| **Spreads** | Typically larger | Very tight (0.1-2 pips for majors) |
| **Correlation** | Stock-specific | Strong correlations between related pairs |
| **Data Frequency** | Tick/minute data | Tick data crucial (1-minute bars insufficient) |

---

## Part 2: Required Configuration Changes by Agent

### 2.1 Market Analyst Agent

**Current State:**
- Analyzes technical indicators (SMA, EMA, MACD, RSI, Bollinger Bands, ATR, VWMA)
- Focuses on single instrument price action
- Uses 50-day, 200-day, and 10-period EMAs

**Forex Adaptations:**

1. **Technical Indicators (Enhanced for Forex)**
   - Keep core indicators but adjust periods for forex timeframes
   - Add forex-specific indicators:
     - **ADX (Average Directional Index)**: Measures trend strength (critical for range-bound forex)
     - **Stochastic Oscillator**: Better for non-trending markets
     - **Fibonacci Retracements**: Key support/resistance levels
     - **Pivot Points**: Daily pivots crucial in forex
     - **CCI (Commodity Channel Index)**: Cyclical strength indicator
   
2. **Timeframe Strategy**
   - Support multiple timeframes: 1H, 4H, Daily, Weekly
   - Add timeframe hierarchy (Weekly > Daily > 4H > 1H analysis)
   - Confluence when all timeframes align

3. **Currency Pair Specific Analysis**
   - Identify pair category (Major: EUR/USD, GBP/USD, etc.)
   - Adjust recommendations based on pair correlations
   - Factor in carry trade dynamics (interest rate differentials)

**Configuration Changes:**
```python
"technical_indicators_enabled": [
    "RSI", "MACD", "Bollinger Bands", "ATR", "VWMA",  # Core
    "ADX", "Stochastic", "Fibonacci", "Pivot Points", "CCI"  # Forex-specific
],
"indicator_periods": {
    "sma_short": 9,      # Adjusted for forex
    "sma_medium": 21,    # Weekly equivalent on 4H
    "sma_long": 55,      # Multi-week trend
    "rsi_period": 14,    # Standard
    "atr_period": 14,    # Standard
    "adx_period": 14     # New for forex
},
"timeframes": ["1H", "4H", "Daily", "Weekly"],
"cross_timeframe_analysis": True
```

---

### 2.2 News Analyst Agent

**Current State:**
- Analyzes company-specific news and announcements
- Uses financial news data

**Forex Adaptations:**

1. **Macroeconomic News Focus**
   - **Central Bank Statements**: ECB, Fed, BoE, BoJ decisions
   - **Economic Calendar Events**: 
     - NFP (Non-Farm Payroll) - biggest for USD
     - CPI, PPI inflation data
     - GDP releases
     - Interest rate decisions
   - **Geopolitical Events**: Trade wars, Brexit-like events, sanctions
   - **Commodity Prices**: Oil (USD pairs), Gold (carries/safe-haven)

2. **News Source Integration**
   - Economic calendar data (Investing.com, TradingEconomics API)
   - Central bank communication monitoring
   - News sentiment analysis specific to currencies
   - Real-time alerts for high-impact releases

3. **Impact Assessment**
   - Classify news by impact level (LOW, MEDIUM, HIGH)
   - Historical volatility patterns around specific news
   - Correlation with currency pair movements
   - Pre-announcement vs post-announcement behavior

**Configuration Changes:**
```python
"forex_news_sources": [
    "central_bank_statements",
    "economic_calendar",
    "geopolitical_events",
    "commodity_prices",
    "interest_rate_decisions"
],
"high_impact_events": {
    "UFD": ["NFP", "FOMC", "ECB Rate Decision", "CPI", "GDP"],
    "GBP": ["BoE Rate Decision", "Brexit Updates", "Inflation Data"],
    "JPY": ["BoJ Decisions", "Carry Trade Unwinding"],
    "CHF": ["SNB Interventions", "Safe-Haven Demand"]
},
"news_weight_in_decision": 0.25  # Higher than equities due to macro events
```

---

### 2.3 Fundamental Analyst Agent

**Current State:**
- Analyzes company financial statements (P/E ratio, earnings, debt, etc.)
- Long-term value investing approach

**Forex Adaptations:**

1. **Interest Rate Differential Analysis (Critical for Forex)**
   - Compare central bank policy rates across currency pairs
   - PPP (Purchasing Power Parity) calculations
   - Real interest rate differentials (inflation-adjusted)
   - Forward guidance from central banks

2. **Macroeconomic Fundamentals**
   - GDP growth rates and trends
   - Inflation rates (CPI, PPI)
   - Trade balance and current account data
   - Unemployment rates (especially jobless claims for USD)
   - Debt-to-GDP ratios
   - Reserve currency strength

3. **Carry Trade Analysis**
   - Interest rate spreads between pairs
   - Funding currency (typically JPY, CHF)
   - Rollover (overnight) swap calculations
   - Risk of carry unwinding

**Configuration Changes:**
```python
"fundamental_metrics": {
    "primary": [
        "interest_rate_differential",
        "inflation_gap",
        "economic_growth_differential",
        "trade_balance",
        "current_account"
    ],
    "secondary": [
        "ppp_analysis",
        "debt_to_gdp",
        "unemployment_rate",
        "reserve_currency_strength"
    ]
},
"carry_trade_enabled": True,
"ppp_target_estimation": True
```

---

### 2.4 Social Media Sentiment Analyst Agent

**Current State:**
- Analyzes social media sentiment about specific stocks
- Tracks retail investor sentiment

**Forex Adaptations:**

1. **Identify Sentiment Sources**
   - Twitter/X for forex traders' opinions
   - Reddit (r/forex, r/wallstreetbets)
   - TradingView community analysis
   - Sentiment from forex-specific platforms

2. **Sentiment Interpretation**
   - Identify "retail crowd" vs "institutional" positions
   - Detect contrarian signals (when retail is wrong)
   - Crowded trades (warning sign for reversals)
   - Sentiment divergence across pairs

3. **Institutional Positioning**
   - CoT (Commitment of Traders) reports
   - Large speculative net positioning
   - Commercial hedger positioning shifts

**Configuration Changes:**
```python
"social_sentiment_sources": [
    "twitter_forex_traders",
    "reddit_forex_communities",
    "tradingview_community",
    "cot_reports"
],
"sentiment_interpretation": {
    "extreme_bullish": [75, 100],     # Potential reversal
    "bullish": [50, 75],
    "neutral": [40, 60],
    "bearish": [25, 50],
    "extreme_bearish": [0, 25]        # Potential reversal
},
"cot_weight": 0.20
```

---

### 2.5 Bull & Bear Researchers

**Current State:**
- Generate bullish and bearish arguments using available data
- Used for debate mechanism

**Forex Adaptations:**

1. **Bull Case (Long EUR/USD Example)**
   - EU economic growth outpacing US
   - ECB holding rates higher longer
   - Risk appetite increasing (good for EUR)
   - Technical breakouts on daily chart

2. **Bear Case (Short EUR/USD Example)**
   - US economic resilience supporting USD
   - Fed rates higher than ECB
   - Geopolitical risk (Ukraine) boosting USD
   - Technical resistance at key levels

**Configuration Changes:**
```python
"bull_bear_debate_factors": [
    "interest_rate_differential",
    "economic_growth_differential",
    "risk_sentiment_direction",
    "technical_levels",
    "carry_trade_dynamics",
    "central_bank_guidance",
    "geopolitical_factors"
],
"debate_weight_distribution": {
    "macroeconomic": 0.35,
    "technical": 0.30,
    "sentiment": 0.15,
    "carry_trade": 0.10,
    "geopolitical": 0.10
}
```

---

### 2.6 Risk Management Agents (Debators)

**Current State:**
- Aggressive: Maximize returns with high leverage and risk
- Conservative: Minimize drawdowns with tight stops
- Neutral: Balance risk and reward

**Forex Adaptations:**

1. **Position Sizing for Leverage**
   - Account for available leverage (typically 50:1 in US, higher in other regions)
   - Calculate maximum position size based on equity
   - Kelly Criterion for optimal risk
   - Maximum risk per trade (typically 1-2% of account)

2. **Forex-Specific Risk Management**
   - **Gap Risk**: Weekend gaps can be substantial in forex
   - **Liquidity Risk**: During Asian session, some pairs less liquid
   - **Slippage**: Consider bid-ask spread and slippage on execution
   - **Margin Calls**: Real risk with leverage
   - **Overnight Risk**: Holding positions during major sessions
   - **Currency Conversion Risk**: For non-native currency traders

3. **Stop Loss & Take Profit Rules**
   - Aggressive: 5-10 pips (micro risk)
   - Conservative: 20-50 pips (macro risk)
   - Neutral: 15-30 pips
   - Adjust based on pair volatility (ATR)
   - Trailing stops for trending markets

**Configuration Changes:**
```python
"risk_management_params": {
    "max_leverage": 50,                    # Regulated US brokers
    "max_risk_per_trade": 0.02,           # 2% of account
    "max_account_risk": 0.05,             # 5% max daily drawdown
    "account_size": 10000,                # Base account assumption
    
    "aggressive": {
        "leverage_usage": 0.80,           # Use 80% of available leverage
        "stop_loss_pips": 8,              # Very tight
        "take_profit_ratio": 1.5,         # 1:1.5 risk-reward
        "position_size_pct": 0.03         # 3% per trade
    },
    "conservative": {
        "leverage_usage": 0.30,           # Use 30% of available leverage
        "stop_loss_pips": 40,             # Wider stops
        "take_profit_ratio": 1.0,         # 1:1 risk-reward
        "position_size_pct": 0.01         # 1% per trade
    },
    "neutral": {
        "leverage_usage": 0.50,           # Use 50% of available leverage
        "stop_loss_pips": 20,             # Medium stops
        "take_profit_ratio": 1.2,         # 1:1.2 risk-reward
        "position_size_pct": 0.02         # 2% per trade
    },
    
    "gap_risk_handling": "reduce_before_weekend",
    "overnight_risk_management": True,
    "liquidity_aware_execution": True
}
```

---

### 2.7 Portfolio Manager Agent

**Current State:**
- Manages multiple stock positions
- Rebalancing logic

**Forex Adaptations:**

1. **Multi-Pair Portfolio Management**
   - Managing multiple currency pairs simultaneously
   - Correlation matrix between pairs (EUR/USD vs GBP/USD are correlated)
   - Hedging strategies (e.g., if long EUR, reduce GBP exposure)
   - Diversification across pair categories

2. **Session-Based Management**
   - Asian session pairs (USD/JPY)
   - European session pairs (EUR/USD, GBP/USD)
   - American session pairs (USD/CAD, USD/MXN)
   - Optimize for liquidity in active sessions

3. **Currency Exposure Monitoring**
   - Track net exposure to each currency (USD, EUR, GBP, JPY, etc.)
   - Balance between long and short exposures
   - Monitor correlation breakdown

**Configuration Changes:**
```python
"portfolio_params": {
    "max_active_pairs": 5,
    "max_exposure_single_currency": 0.30,  # 30% max in one currency
    "correlation_threshold": 0.70,
    "rebalance_frequency": "daily",
    "session_optimization": True,
    "sessions": {
        "asian": ["USD/JPY", "AUD/USD"],
        "european": ["EUR/USD", "GBP/USD", "EUR/GBP"],
        "american": ["USD/CAD", "USD/MXN"]
    }
}
```

---

### 2.8 Trader/Execution Agent

**Current State:**
- Makes final BUY/SELL/HOLD decision for individual stock
- Considers all analyst inputs

**Forex Adaptations:**

1. **Decision Framework**
   - BUY (go LONG): All factors aligned for appreciation
   - SELL (go SHORT): All factors aligned for depreciation
   - HOLD: Mixed signals or wait for confirmation
   - WAIT: Ahead of major economic news

2. **Position Entry/Exit**
   - Entry: When confidence threshold reached (>70%)
   - Exit: Based on stops/profit targets or reversal signals
   - Partial exits: Scale out of winners
   - Re-entries: After breakouts from consolidation

3. **Order Management**
   - Market orders vs Limit orders (prefer limit for better fills)
   - Scale in/out strategies
   - Reduce overnight exposure before weekends
   - Track filled price vs planned entry

**Configuration Changes:**
```python
"trader_decision_params": {
    "confidence_threshold": 0.70,
    "entry_types": ["market", "limit"],
    "exit_strategies": [
        "stop_loss",
        "take_profit",
        "reversal_signal",
        "news_event"
    ],
    "scale_out_enabled": True,
    "scale_out_levels": [0.33, 0.66, 1.0],  # Exit 1/3, 2/3, close
    "partial_order_sizes": [0.25, 0.50, 0.25]
}
```

---

## Part 3: Data Feeds & Tools Configuration

### 3.1 Required Data Sources

```python
"data_vendors": {
    # Current stock data (keep if hybrid)
    "core_stock_apis": "yfinance",
    
    # NEW: Forex-specific data
    "forex_data": "yfinance",  # Alternative: alpha_vantage, oanda, ib
    "economic_calendar": "trading_economics_api",
    "cot_reports": "cftc_official",
    "central_bank_statements": "official_feeds",
    "commodity_prices": "yfinance",  # Gold, Oil for USD analysis
    "interest_rates": "fred_api",    # US Federal Reserve
    "inflation_data": "bls_api"      # Bureau of Labor Statistics
},
```

### 3.2 New Tools Required

```python
"forex_tools": [
    # Technical Analysis
    "get_forex_ohlc",              # Forex OHLC data
    "get_technical_indicators",    # Existing, but with forex params
    "get_pivot_points",            # Daily pivot calculations
    "get_fibonacci_levels",        # Fib retracements for key levels
    
    # Fundamental Analysis
    "get_central_bank_rates",      # Current policy rates
    "get_economic_calendar",       # Upcoming economic releases
    "get_interest_rate_diff",      # Differential analysis
    "get_inflation_data",          # CPI, PPI figures
    "get_gdp_growth",              # Economic growth metrics
    
    # Sentiment & Positioning
    "get_cot_reports",             # Commitment of traders
    "get_sentiment_index",         # Aggregated retail sentiment
    
    # Execution
    "get_bid_ask_spread",          # Real-time spread data
    "get_forex_liquidity",         # Liquidity assessment
    
    # Risk Management
    "calculate_position_size",     # Kelly criterion based
    "calculate_margin_required",   # Leverage calculations
]
```

---

## Part 4: Configuration Structure

### 4.1 Complete Forex Default Config

```python
# tradingagents/forex_default_config.py

import os

FOREX_DEFAULT_CONFIG = {
    # Project & directories
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_cache_dir": "./dataflows/forex_data_cache",
    
    # LLM Settings (keep as inherited from DEFAULT_CONFIG)
    "llm_provider": "openai",
    "deep_think_llm": "gpt-5.4",
    "quick_think_llm": "gpt-5.4-mini",
    
    # Forex-Specific Market Settings
    "trading_mode": "forex",
    "base_currency": "USD",  # Account currency
    "account_size": 10000,   # Starting capital
    "account_currency": "USD",
    
    # Agent Selection & Role Assignment
    "selected_analysts": [
        "market",        # Technical analysis
        "fundamentals",  # Interest rates, growth, inflation
        "news",         # Economic calendar, central bank
        "social"        # Market sentiment, CoT
    ],
    
    # Debate Settings
    "max_debate_rounds": 2,
    "max_risk_discuss_rounds": 2,
    
    # Data Vendor Configuration
    "data_vendors": {
        "forex_ohlc": "yfinance",              # or: oanda, alpha_vantage
        "technical_indicators": "yfinance",
        "economic_calendar": "trading_economics",
        "central_bank_data": "official",
        "cot_reports": "cftc",
        "commodity_data": "yfinance",
        "interest_rates": "fred_api",
    },
    
    # Technical Indicators Configuration
    "technical_indicators_config": {
        "enabled_indicators": [
            "RSI", "MACD", "Bollinger_Bands", "ATR", "ADX",
            "Stochastic", "Pivot_Points", "Fibonacci", "CCI"
        ],
        "periods": {
            "sma_short": 9,
            "sma_medium": 21,
            "sma_long": 55,
            "rsi_period": 14,
            "atr_period": 14,
            "adx_period": 14,
            "stoch_period": 14,
            "cci_period": 20
        },
        "timeframes": ["1H", "4H", "Daily", "Weekly"],
        "cross_timeframe_analysis": True
    },
    
    # Risk Management Configuration
    "risk_management": {
        "max_leverage": 50,
        "max_risk_per_trade_pct": 0.02,
        "max_daily_loss_pct": 0.05,
        
        "aggressive_profile": {
            "leverage_usage": 0.80,
            "stop_loss_pips": 8,
            "take_profit_ratio": 1.5,
            "position_size_pct": 0.03
        },
        "conservative_profile": {
            "leverage_usage": 0.30,
            "stop_loss_pips": 40,
            "take_profit_ratio": 1.0,
            "position_size_pct": 0.01
        },
        "neutral_profile": {
            "leverage_usage": 0.50,
            "stop_loss_pips": 20,
            "take_profit_ratio": 1.2,
            "position_size_pct": 0.02
        },
    },
    
    # Portfolio Settings
    "portfolio": {
        "max_active_pairs": 5,
        "max_exposure_per_currency": 0.30,
        "correlation_threshold": 0.70,
        "rebalance_frequency": "daily"
    },
    
    # Macro Analysis Settings
    "macro_analysis": {
        "interest_rate_analysis": True,
        "inflation_analysis": True,
        "growth_analysis": True,
        "carry_trade_analysis": True,
        "ppp_analysis": True,
        
        "key_economic_indicators": {
            "USD": ["NFP", "CPI", "FOMC", "Fed Funds Rate", "GDP"],
            "EUR": ["ECB Rate", "Inflation", "GDP", "PMI"],
            "GBP": ["BoE Rate", "CPI", "Retail Sales"],
            "JPY": ["BoJ Rate", "Trade Balance", "Nikkei 225"],
            "CAD": ["BoC Rate", "Labour Force Survey", "CPI"]
        }
    },
    
    # News & Sentiment Settings
    "news_sentiment": {
        "monitor_economic_calendar": True,
        "high_impact_only": False,  # Process all events
        "news_weight": 0.25,
        "sentiment_weight": 0.15,
        "cot_weight": 0.20
    },
    
    # Trading Session Settings
    "sessions": {
        "enabled": True,
        "optimized_pairs": {
            "asian": ["USD/JPY", "AUD/USD", "USD/SGD"],
            "european": ["EUR/USD", "GBP/USD", "EUR/GBP", "USD/CHF"],
            "american": ["USD/CAD", "USD/MXN", "USD/BRL"]
        }
    },
    
    # Output Settings
    "output_language": "English",
    "debug_mode": False,
    "memory_enabled": True
}
```

---

## Part 5: Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Create `forex_default_config.py` with all forex-specific parameters
- [ ] Extend data tools to support forex data feeds
- [ ] Modify `get_stock_data` → `get_forex_data` with pair support
- [ ] Update technical indicator calculations for forex timeframes
- [ ] Add economic calendar data source integration

### Phase 2: Agent Adaptations (Week 3-4)
- [ ] **Market Analyst**: Add ADX, Fibonacci, Pivot Points, timeframe hierarchy
- [ ] **Fundamentals Analyst**: Implement interest rate differential, PPP, inflation gap
- [ ] **News Analyst**: Economic calendar integration, central bank monitoring
- [ ] **Social Sentiment**: CoT reports, forex-specific sentiment sources
- [ ] **Bull/Bear Researchers**: Update argument generation for forex factors

### Phase 3: Risk Management (Week 5)
- [ ] Adapt Risk Debators for leverage management
- [ ] Implement position sizing algorithms
- [ ] Add overnight & weekend risk handling
- [ ] Session-based position management
- [ ] Margin call prevention logic

### Phase 4: Integration & Testing (Week 6-7)
- [ ] Update `TradingAgentsGraph` to load forex config
- [ ] Create forex-specific Example entry point (`forex_main.py`)
- [ ] Backtesting framework for forex pairs
- [ ] Paper trading integration
- [ ] Live trading safeguards

### Phase 5: Documentation & Deployment (Week 8)
- [ ] Update README with forex-specific instructions
- [ ] Agent configuration examples
- [ ] Risk management guidelines
- [ ] Forex-specific troubleshooting guide
- [ ] Deployment checklist

---

## Part 6: Quick Start - Using Forex Configuration

```python
# forex_main.py (Example)

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.forex_default_config import FOREX_DEFAULT_CONFIG

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create custom config (override as needed)
config = FOREX_DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-5.4"
config["quick_think_llm"] = "gpt-5.4-mini"

# Initialize trading agents for Forex
ta = TradingAgentsGraph(
    selected_analysts=["market", "fundamentals", "news", "social"],
    debug=True,
    config=config
)

# Analyze EUR/USD pair with specific date
_, decision = ta.propagate(
    currency_pair="EUR/USD",
    trade_date="2024-05-10",
    timeframe="4H"
)

print(decision)

# Reflect on past performance
# ta.reflect_and_remember(position_return_pips=45)
```

---

## Part 7: Currency Pair Categories & Strategy Adjustments

### Major Pairs (Most Liquid)
- EUR/USD, USD/JPY, GBP/USD, USD/CHF, USD/CAD, AUD/USD, NZD/USD

**Strategy**: Tighter spreads, more liquidity, suitable for all trading styles

### Minor Pairs (Cross Pairs)
- EUR/GBP, EUR/JPY, GBP/JPY, EUR/CHF

**Strategy**: Less liquid, wider spreads, suitable for longer timeframes

### Exotic Pairs
- USD/TRY, USD/BRL, USD/MXN, USD/SGD

**Strategy**: Much wider spreads, lower liquidity, use wider stops, avoid during low-liquidity sessions

---

## Part 8: Key Monitoring Parameters

Create monitoring dashboard for:

1. **Real-time Pair Analysis**
   - Current price, bid-ask spread, volatility (ATR)
   - Technical levels (support, resistance, pivots)
   - Key technical indicators
   - Time to next high-impact news

2. **Portfolio Health**
   - Total open positions and exposure
   - Current margin usage
   - Daily P&L and % return
   - Maximum drawdown

3. **Economic Calendar**
   - Next 7 days of economic releases
   - Expected vs. Previous vs. Forecast
   - Actual releases and impacts

4. **Central Bank Monitoring**
   - Current policy rates
   - Next decision dates
   - Guidance and tone changes

---

## Conclusion

This plan transforms the TradingAgents framework from equities-focused to **forex-specialized** by:

1. ✅ Adapting all agents for macro-driven, 24/5 markets
2. ✅ Incorporating forex-specific data sources and tools
3. ✅ Implementing leverage-aware risk management
4. ✅ Managing multiple correlated currency pairs
5. ✅ Monitoring economic calendars and central banks
6. ✅ Supporting multiple trading timeframes and sessions

Follow the implementation roadmap for a systematic approach to full forex integration.

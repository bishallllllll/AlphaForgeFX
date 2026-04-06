# AlphaForgeFX Forex Configuration - Quick Reference Guide

## 📋 Overview

This guide provides a quick reference for configuring the AlphaForgeFX agents for forex trading.

---

## 🎯 Configuration Quick Links

| Document | Purpose |
|----------|---------|
| [FOREX_AGENT_CONFIG_PLAN.md](FOREX_AGENT_CONFIG_PLAN.md) | Complete strategic plan with 8-week roadmap |
| [FOREX_IMPLEMENTATION_EXAMPLES.md](FOREX_IMPLEMENTATION_EXAMPLES.md) | Code examples and implementation details |
| [tradingagents/forex_default_config.py](tradingagents/forex_default_config.py) | Ready-to-use configuration file |
| [forex_main.py](forex_main.py) | Example entry point for analysis |

---

## 🚀 Quick Start (5 minutes)

### Step 1: Create Forex Config File
Create `tradingagents/forex_default_config.py` with the contents from FOREX_IMPLEMENTATION_EXAMPLES.md

### Step 2: Create Entry Point
Create `forex_main.py` with the example from FOREX_IMPLEMENTATION_EXAMPLES.md

### Step 3: Run Analysis
```bash
python forex_main.py
```

---

## 🔧 Key Configuration Parameters

### Account & Leverage
```python
"account_size": 10000,              # Starting capital
"max_leverage": 50,                 # Maximum allowed leverage
"base_currency": "USD",             # Account currency
```

### Risk Profiles

#### Aggressive
- Leverage: 80% usage (40:1)
- Stop Loss: 8 pips
- Position Size: 3% per trade
- Best For: Experienced traders with high risk tolerance

#### Neutral (Recommended Start)
- Leverage: 50% usage (25:1)
- Stop Loss: 20 pips
- Position Size: 2% per trade
- Best For: Balanced risk-reward

#### Conservative
- Leverage: 30% usage (15:1)
- Stop Loss: 40 pips
- Position Size: 1% per trade
- Best For: Capital preservation focus

### Technical Analysis
```python
"enabled_indicators": [
    "RSI",              # Momentum (overbought/oversold)
    "MACD",             # Trend & momentum
    "ADX",              # Trend strength (14+ = trending)
    "Bollinger_Bands",  # Volatility & support/resistance
    "Fibonacci",        # Key price levels
    "Pivot_Points",     # Daily support/resistance
    "Stochastic",       # Oscillator (range-bound markets)
    "CCI"               # Cyclic strength indicator
]

"timeframes": ["1H", "4H", "Daily", "Weekly"]
"cross_timeframe_analysis": True  # Require alignment across timeframes
```

### Macroeconomic Weights
```python
"macro_weights": {
    "interest_rates": 0.35,         # Most important factor
    "inflation": 0.20,
    "growth": 0.15,
    "trade_balance": 0.10,
    "carry_trade": 0.10,
    "geopolitical": 0.10
}
```

### Portfolio Management
```python
"max_active_pairs": 5,              # Maximum pairs to trade
"max_exposure_per_currency": 0.30,  # Max 30% in one currency
"preferred_pairs": [
    "EUR/USD",          # Most traded, tightest spreads
    "GBP/USD",
    "USD/JPY",
    "USD/CAD",
    "AUD/USD"
]
```

---

## 📊 Agent Configuration by Type

### Market Analyst
**Focus**: Technical indicators and price action
- Analyzes 1H → 4H → Daily → Weekly hierarchy
- Uses 8 complementary indicators
- Identifies support, resistance, and trend
- Measures trend strength (ADX)
- **Output**: Technical analysis report with confidence level

### Fundamentals Analyst
**Focus**: Macroeconomic factors
- Analyzes interest rate differentials
- Tracks inflation gaps between currencies
- Assesses carry trade dynamics
- Evaluates PPP (purchasing power parity)
- **Output**: Fundamental analysis with medium-term outlook

### News Analyst
**Focus**: Economic calendar and central bank actions
- Monitors high-impact releases
- Tracks central bank decisions and guidance
- Watches geopolitical events
- Evaluates pre/post-announcement behavior
- **Output**: News impact assessment and forecast

### Social/Sentiment Analyst
**Focus**: Market positioning and retail sentiment
- Analyzes CoT (Commitment of Traders) reports
- Tracks retail trader sentiment
- Identifies crowded trades (contrarian signals)
- Monitors positioning divergences
- **Output**: Sentiment summary with contrarian signals

### Bull & Bear Researchers
**Focus**: Pro and con arguments
- Bull Research: Why price should go UP
- Bear Research: Why price should go DOWN
- Based on all available data
- **Output**: Debate arguments for final decision

### Risk Debaters (Aggressive/Conservative/Neutral)
**Focus**: Risk management recommendations
- Aggressive: Maximize returns with higher leverage
- Conservative: Minimize losses with tight stops
- Neutral: Balance both objectives
- **Output**: Risk-adjusted position sizing and stops

### Trader/Execution Agent
**Focus**: Final decision and execution
- Synthesizes all analyst inputs
- Makes BUY / SELL / HOLD decision
- Determines entry and exit levels
- **Output**: FINAL TRANSACTION PROPOSAL with confidence

---

## 🌍 Currency Pair Setup

### Major Pairs (Recommended Start)
```python
"preferred_pairs": [
    "EUR/USD",      # Most liquid, 1.06-1.08 typical range
    "GBP/USD",      # Volatile, 1.25-1.30 typical range
    "USD/JPY",      # Carry currency, 140-150 typical range
    "USD/CAD",      # Oil correlated, 1.25-1.35 typical range
    "AUD/USD"       # Risk sentiment indicator, 0.60-0.70 typical
]
```

### Trading Sessions
```python
"sessions": {
    "asian": {              # 21:00-08:00 UTC
        "pairs": ["USD/JPY", "AUD/USD"],
        "liquidity": "medium"
    },
    "european": {           # 07:00-16:00 UTC (BEST)
        "pairs": ["EUR/USD", "GBP/USD", "EUR/GBP"],
        "liquidity": "very_high"
    },
    "american": {           # 12:00-21:00 UTC
        "pairs": ["USD/CAD", "USD/MXN"],
        "liquidity": "high"
    },
    "overlap": {            # 12:00-16:00 UTC (BEST FOR VOLUME)
        "pairs": "all_majors",
        "liquidity": "highest"
    }
}
```

---

## 📈 Trading Logic Flow

```
1. DATA COLLECTION
   ├─ Get OHLC and indicators for all timeframes
   ├─ Fetch economic calendar events
   ├─ Get interest rate data
   └─ Pull CoT reports and sentiment

2. AGENT ANALYSIS (Parallel)
   ├─ Market Analyst → Technical Report
   ├─ Fundamentals Analyst → Macro Report
   ├─ News Analyst → Event Report
   ├─ Social Sentiment → Positioning Report
   └─ Bull/Bear Researchers → Debate

3. RISK ASSESSMENT
   ├─ Aggressive Debater: Aggressive case
   ├─ Conservative Debater: Conservative case
   └─ Neutral Debater: Balanced case

4. FINAL DECISION
   ├─ Trader synthesizes all inputs
   ├─ Calculates confidence score
   └─ Proposes: BUY / SELL / HOLD

5. EXECUTION (if confidence > 70%)
   ├─ Calculate position size
   ├─ Set stop loss and take profit
   ├─ Place order
   └─ Log trade and lessons
```

---

## ⚙️ Configuration Checklist

Before running forex analysis:

- [ ] **LLM Setup**
  - [ ] OpenAI API key in `.env`
  - [ ] Model availability confirmed (gpt-5.4, gpt-5.4-mini)

- [ ] **Data Sources**
  - [ ] yfinance working for forex data
  - [ ] Research economic calendar API (TradingEconomics free or paid)
  - [ ] FRED API for interest rates (free)
  - [ ] CoT reports accessible

- [ ] **Initial Configuration**
  - [ ] Account size set correctly
  - [ ] Risk profile selected (aggressive/neutral/conservative)
  - [ ] Preferred pairs selected
  - [ ] Leverage limits configured

- [ ] **Risk Management**
  - [ ] Stop loss values set
  - [ ] Position sizing math verified
  - [ ] Max daily loss limit configured
  - [ ] Margin requirements calculated

- [ ] **Directories**
  - [ ] `./results/forex/` created
  - [ ] `./dataflows/forex_data_cache/` created
  - [ ] Log files writable

- [ ] **Testing**
  - [ ] Configuration file loads without errors
  - [ ] Single pair analysis completes
  - [ ] All agents produce output
  - [ ] Decision logic works

---

## 🐛 Troubleshooting

### Issue: "No module named forex_default_config"
**Solution**: Make sure file is in `tradingagents/` directory and check Python path

### Issue: "Cannot get forex data for EURUSD"
**Solution**: Try `EUR/USD` format (with slash), check yfinance ticker format

### Issue: LLM errors mid-analysis
**Solution**: Check API key, rate limits, model availability

### Issue: Position sizing calculations wrong
**Solution**: Verify pip value for pair, check leverage multiplier (50:1 for USD)

### Issue: Risk profile not respected
**Solution**: Check debater agents are using override parameters, not defaults

---

## 📚 Key Forex Concepts

| Term | Definition |
|------|-----------|
| **Pip** | Smallest price move (0.0001 for most pairs) |
| **Spread** | Bid-ask difference (0.2 pips = 2 pips for EUR/USD) |
| **Leverage** | Ratio of position to account (50:1, 100:1, 500:1) |
| **Carry Trade** | Profit from interest rate differential |
| **Support/Resistance** | Price levels where buying/selling climaxes |
| **Pivot Points** | Daily levels calculated from previous day's OHLC |
| **ADX** | Trend strength indicator (14+ indicates trending) |
| **Risk/Reward Ratio** | Profit target vs stop loss distance |
| **CoT Reports** | Commitments of Traders positioning data |
| **Slippage** | Actual fill price vs expected price |

---

## 🎓 Learning Resources

### Technical Analysis
- RSI: Measure overbought (>70) and oversold (<30)
- MACD: Momentum crossovers signal trend changes
- ADX: >20 = trending, <20 = ranging market
- Fibonacci: 61.8%, 50%, 38.2%, 23.6% retracements are natural support/resistance

### Fundamental Analysis
- Interest Rate Differentials: Higher rates attract capital (currency strength)
- Inflation Gap: Widening gap supports currency appreciation
- PPP: Long-term price level equalization between currencies
- Carry Trade: Borrow in JPY/CHF (low rates), invest in AUD/NZD (high rates)

### Economic Calendar
- **NFP** (First Friday): Most important USD data
- **ECB Decisions** (Every 6 weeks): Affects EUR heavily
- **BoJ Interventions**: Can spike move 200+ pips instantly
- **CPI Releases**: Inflation data moves markets significantly

### Risk Management
- **Kelly Criterion**: Optimal position sizing for expected win rate
- **Martingale**: AVOID - doubles risk after losing trades
- **Risk/Reward**: Minimize 1:1, target 1:1.5 or better
- **Max Daily Loss**: Stop trading once daily limit hit

---

## 🔗 Integration with Main Framework

The forex configuration integrates seamlessly:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.forex_default_config import FOREX_DEFAULT_CONFIG

# Standard initialization - just pass forex config
ta = TradingAgentsGraph(config=FOREX_DEFAULT_CONFIG)

# All existing methods work with forex pairs
_, decision = ta.propagate("EUR/USD", "2024-05-10")
```

---

## 📞 Support

For issues or questions:

1. Check [FOREX_AGENT_CONFIG_PLAN.md](FOREX_AGENT_CONFIG_PLAN.md) for strategy details
2. Review [FOREX_IMPLEMENTATION_EXAMPLES.md](FOREX_IMPLEMENTATION_EXAMPLES.md) for code
3. Verify configuration files match the templates
4. Check `.env` file for API keys
5. Review LLM provider documentation for rate limits

---

## 📋 Configuration Files Summary

| File | Purpose | Lines |
|------|---------|-------|
| `FOREX_AGENT_CONFIG_PLAN.md` | Strategic planning document | 550+ |
| `FOREX_IMPLEMENTATION_EXAMPLES.md` | Code examples and implementations | 700+ |
| `tradingagents/forex_default_config.py` | Configuration class | 400+ |
| `forex_main.py` | Entry point Example | 150+ |
| `tradingagents/agents/utils/forex_tools.py` | Forex-specific tools | 200+ |
| `FOREX_QUICK_REFERENCE.md` | This file | 400+ |

**Total Documentation**: 2,400+ lines of detailed guidance

---

## ✅ Next Steps

1. **Review** the configuration plan
2. **Create** the forex_default_config.py file
3. **Test** with a single pair (EUR/USD recommended)
4. **Backtest** before paper trading
5. **Paper trade** before live trading
6. **Monitor** results and refine parameters

Good luck with your forex trading! 🚀

# Phase 1: Forex Data Gathering Pipeline

## Overview

Phase 1 is the **Data Gathering & Analysis** phase where multiple specialized analysts examine different aspects of a currency pair before trading decisions are made.

For **forex trading**, Phase 1 consists of:

1. **📊 Forex Market Analyst** - Technical analysis
2. **💬 Social Media Analyst** - Sentiment analysis (slightly adapted for forex)
3. **📰 News Analyst** - News impact analysis
4. **💱 Macro Analyst** - Macroeconomic fundamentals *(NEW for forex)*

## Phase 1 Pipeline Architecture

```
START
  ↓
[Forex Market Analyst] ← Technical indicators, price action, support/resistance
  ↓
[Social Media Analyst] ← Sentiment from forex community/traders
  ↓
[News Analyst] ← Central bank news, economic news, geopolitical events
  ↓
[Macro Analyst] ← Interest rates, economic calendar, central bank policy
  ↓
→ Bull Researcher (Phase 2)
```

---

## 1. Forex Market Analyst

**File:** `tradingagents/agents/analysts/forex_market_analyst.py`

**Purpose:** Technical analysis of the currency pair using indicators and price action

**Tools Available:**
- `get_stock_data` - Fetch OHLCV price data
- `get_indicators` - Calculate technical indicators

**Key Indicators for Forex:**
- **Trend:** 50 SMA, 200 SMA, 10 EMA
- **Momentum:** MACD, RSI
- **Volatility:** ATR, Bollinger Bands

**Analysis Focus:**
- Trend direction (uptrend, downtrend, sideways)
- Support and resistance levels
- Momentum strength
- Volatility levels and potential breakouts
- Timeframe confluence (4H, Daily, Weekly alignment)

**Example Usage:**
```python
from tradingagents.agents import create_forex_market_analyst

market_analyst = create_forex_market_analyst(llm)

# In the graph state:
state = {
    "messages": [...],
    "trade_date": "2024-02-02",
    "instrument": "EURUSD",  # Currency pair
    "company_of_interest": "EURUSD"  # Alternative key
}

result = market_analyst(state)
# Returns: {"messages": [...], "market_report": "..."}
```

---

## 2. Social Media Analyst

**File:** `tradingagents/agents/analysts/social_media_analyst.py`

**Purpose:** Assess sentiment and positioning from forex traders on social media

**Tools Available:**
- `get_social_media_sentiment` - Fetch sentiment from Twitter, Reddit, trading forums
- `get_position_data` - Aggregate trader positioning data (COT reports)

**Analysis Focus (Forex-Adapted):**
- Retail trader positioning (are most longs or shorts?)
- Sentiment extremes (potential contrarian signals)
- Major events and forex community reaction
- Consensus vs. dissenting views
- Crowd behavior indicators

**Key Differences from Stock Sentiment:**
- Forex traders focus on carry trades, rate differentials
- Strong influence from economic calendar expectations
- Geopolitical events drive rapid sentiment shifts
- CoT (Commitment of Traders) data is crucial for positioning

---

## 3. News Analyst

**File:** `tradingagents/agents/analysts/news_analyst.py`

**Purpose:** Analyze recent news events impacting the currency pair

**Tools Available:**
- `get_global_news` - Fetch macroeconomic and central bank news
- `get_news` - Search specific news queries

**Analysis Focus (Forex-Adapted):**
- Central bank communications and policy signals
- Economic data releases and consensus vs actuals
- Geopolitical developments
- Trade/tariff announcements
- Safe-haven flows and risk sentiment

**Key News Sources for Forex:**
- Central bank press releases (Fed, ECB, BoE, BoJ)
- Macro economic data (NFP, CPI, GDP, PMI)
- Geopolitical events (tensions, elections, trade disputes)
- Currency-specific news (Brexit, euro stability, etc.)

---

## 4. Macro Analyst (NEW for Forex)

**File:** `tradingagents/agents/analysts/macro_analyst.py`

**Purpose:** Deep macroeconomic analysis of both currencies in the pair

**Tools Available:**
- `get_interest_rates()` - Current policy rates and central bank stances
- `get_economic_calendar()` - Upcoming high-impact economic events
- `get_macro_indicators()` - Inflation, GDP, employment, trade balances
- `get_central_bank_policy()` - Policy statements and forward guidance
- `get_geopolitical_risk()` - Political and geopolitical risk factors

**Core Analysis Areas:**

### Interest Rate Analysis
- Compare policy rates between the two currencies
- Assess rate differential (who has higher rates?)
- Identify rate path divergence
- Forward guidance from central banks

Example: EUR 4.25% vs USD 5.25% = 100 bps spread favoring USD

### Inflation Analysis
- Compare inflation rates and trends
- Assess real interest rates (nominal - inflation)
- Project future inflation based on indicators
- Identify which currency central bank is more hawkish/dovish

### Economic Growth
- Compare GDP growth rates
- Assess employment trends
- Review trade balance and current account
- Identify growth divergence

### Central Bank Policy Stance
- Is the central bank done hiking? (Restrictive cycle)
- When will rate cuts begin? (Easing cycle)
- Is policy hawkish or dovish?
- What's the forward guidance?

### Upcoming Events Impact
- NFP release impact on USD
- CPI data impact on EUR
- Central bank meetings and rate decisions
- Major data releases and expected reactions

Example economic calendar entry:
```
2024-02-02 13:30 UTC - US NFP: Forecast 180K, Previous 216K
→ High impact on USD and pairs (EURUSD, GBPUSD)
→ Miss would be bearish for USD; beat would be bullish
```

**Example Usage:**
```python
from tradingagents.agents import create_macro_analyst

macro_analyst = create_macro_analyst(llm)

state = {
    "messages": [...],
    "trade_date": "2024-02-02",
    "instrument": "EURUSD",
    "company_of_interest": "EURUSD"
}

result = macro_analyst(state)
# Returns: {"messages": [...], "macro_report": "..."}
```

---

## Phase 1 Integration into Graph

### Setup in `setup.py`

```python
# Example: Forex-focused Phase 1 configuration
selected_analysts = [
    "forex_market",    # Technical analysis with forex focus
    "social",          # Trader sentiment
    "news",            # News and events
    "macro",           # Macroeconomic analysis (NEW)
]

# In setup_graph():
if "forex_market" in selected_analysts:
    analyst_nodes["forex_market"] = create_forex_market_analyst(
        self.quick_thinking_llm
    )
    delete_nodes["forex_market"] = create_msg_delete()
    tool_nodes["forex_market"] = self.tool_nodes["forex_market"]

if "macro" in selected_analysts:
    analyst_nodes["macro"] = create_macro_analyst(
        self.quick_thinking_llm
    )
    delete_nodes["macro"] = create_msg_delete()
    tool_nodes["macro"] = self.tool_nodes["macro"]
```

### Configuration in `default_config.py`

```python
FOREX_CONFIG = {
    "llm_provider": "anthropic",
    "deep_think_llm": "claude-opus",
    "quick_think_llm": "claude-haiku",
    
    # Phase 1 analysts for forex
    "selected_analysts": ["forex_market", "social", "news", "macro"],
    
    # Currency pair to trade
    "instrument": "EURUSD",
    
    # Other configuration...
}
```

---

## Phase 1 Output

Each analyst in Phase 1 produces a report:

### Market Analyst Report
```
TECHNICAL ANALYSIS REPORT - EURUSD

Trend Analysis:
- Overall: Downtrend on Daily (EUR weakening)
- 200 SMA: 1.1050 (resistance)
- 50 SMA: 1.0950 (key support)
- 10 EMA: Below 50 SMA (bearish alignment)

Support/Resistance:
- Resistance 1: 1.1050 (200 SMA)
- Resistance 2: 1.1100 (24-day high)
- Support 1: 1.0950 (50 SMA)
- Support 2: 1.0900 (25-day low)

Momentum:
- RSI: 35 (approaching oversold)
- MACD: Bearish crossover, histogram negative
- Technical Outlook: Downside bias, but oversold

Key Levels: [1.1100, 1.1050, 1.0950, 1.0900]
```

### Macro Analyst Report
```
MACROECONOMIC ANALYSIS - EURUSD

Interest Rate Analysis:
- USD Rate: 5.25% (Fed holding steady)
- EUR Rate: 4.25% (ECB on hold, may cut later)
- Differential: 100 bps favoring USD (bullish for USD)
- Impact: Positive for USD, negative for EUR

Inflation Context:
- US CPI: 3.1% YoY (down from 3.4%)
- EU CPI: 2.4% YoY (down from 2.8%)
- EUR is already through disinflation; Fed still fighting it

Economic Calendar (Next 2 Weeks):
- Feb 2: US NFP (critical USD catalyst)
- Feb 7: ECB Interest Rate Decision (potential EUR catalyst)
- Feb 14: US CPI (critical USD catalyst)

Central Bank Policy:
- Fed: Pausing hikes, "higher for longer" stance
- ECB: Ready to ease, potential first cut by Q2
- Policy Divergence: ECB easing while Fed holds = EUR weakness

Outlook:
- Macro backdrop favors USD strength
- EUR weakness expected if ECB cuts before Fed
- Watch for divergence to accelerate

Key Macro Themes: [Rate Differential, Disinflation, Policy Divergence]
```

---

## Key Differences: Stock vs. Forex Phase 1

| Aspect | Stock Trading | Forex Trading |
|--------|---------------|---------------|
| **Data Source** | Company fundamentals | Macroeconomic indicators |
| **Primary Driver** | Company earnings & growth | Interest rate differentials |
| **Sentiment** | Retail investor positioning | Forex trader/bank positioning |
| **News Focus** | Company-specific news | Central bank & macro news |
| **Technical** | Similar indicators | Same indicators, different context |
| **Time Horizon** | Days to months | Often shorter (intraday to weeks) |
| **Risk Level** | Leverage varies | Typically high leverage |

---

## Next: Phase 2

Once Phase 1 analysts complete their reports, the pipeline moves to **Phase 2: Research Debate**

- **Bull Researcher** makes the bullish case based on Phase 1 data
- **Bear Researcher** makes the bearish case based on Phase 1 data
- **Research Manager** synthesizes both into a consensus recommendation

---

## Configuration Examples

### Example 1: Aggressive Forex Trading Config
```python
forex_aggressive_config = {
    "selected_analysts": ["forex_market", "macro"],  # Focus on technical + macro
    "instrument": "EURUSD",
    "risk_tolerance": "aggressive",
    "leverage": 10,  # 10:1 leverage
    "position_size_percent": 5,
}
```

### Example 2: Conservative Forex Config
```python
forex_conservative_config = {
    "selected_analysts": ["forex_market", "news", "macro"],  # All analysts
    "instrument": "EURUSD",
    "risk_tolerance": "conservative",
    "leverage": 2,  # 2:1 leverage
    "position_size_percent": 1,
}
```

### Example 3: News-Driven Forex Config
```python
forex_news_config = {
    "selected_analysts": ["macro", "news", "social"],  # Skip technical for event trading
    "instrument": "EURUSD",
    "focus": "economic_calendar",  # Trade around major events
    "risk_tolerance": "moderate",
}
```

---

## Summary

**Phase 1** for forex trading consists of 4 complementary analysts that examine:
1. ✅ **Technical structure** - Entry/exit points
2. ✅ **Trader sentiment** - Positioning and crowd behavior
3. ✅ **News events** - Recent catalysts and upcoming events
4. ✅ **Macroeconomics** - Interest rates, growth, policy, and rate differentials

Together, they provide a complete picture of the currency pair's fundamentals and technicals, setting the stage for the research and trading phases.


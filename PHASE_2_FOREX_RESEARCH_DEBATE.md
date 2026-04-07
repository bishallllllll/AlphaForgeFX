# Phase 2: Forex Research Debate Pipeline

## Overview

Phase 2 is the **Research Debate** phase where bullish and bearish analysts synthesize Phase 1 data into opposing trade recommendations, then debate to reach a consensus viewpoint.

For **forex trading**, Phase 2 consists of:

1. **🐂 Bull Researcher** - Makes the bullish case based on Phase 1 data
2. **🐻 Bear Researcher** - Makes the bearish case based on Phase 1 data
3. **📊 Research Manager** - Synthesizes both arguments into a final recommendation

---

## Phase 2 Pipeline Architecture

```
Phase 1 Outputs:
├─ [Market Report] ← From Forex Market Analyst
├─ [Sentiment Report] ← From Social Media Analyst
├─ [News Report] ← From News Analyst
└─ [Macro Report] ← From Macro Analyst

        ↓

Phase 2 Debate:
├─ [Bull Researcher] ← Analyzes all Phase 1 reports
├─ [Bear Researcher] ← Analyzes all Phase 1 reports
└─ [Debate Back-and-Forth] ← Exchange arguments
        
        ↓
        
[Research Manager] ← Synthesizes into consensus recommendation
        
        ↓
        
Phase 3: Trader Decision
```

---

## Phase 2 Components

### 1. Bull Researcher

**File:** `tradingagents/agents/researchers/bull_researcher.py`

**Purpose:** Build a strong, evidence-based bullish case for trading the currency pair

**Inputs from Phase 1:**
- `state["market_report"]` - Technical analysis from Forex Market Analyst
- `state["sentiment_report"]` - Trader positioning from Social Media Analyst
- `state["news_report"]` - Recent news and events from News Analyst
- `state["macro_report"]` - Macroeconomic analysis from Macro Analyst

**Dynamic Currency Pair Support:**
```python
currency_pair = state.get("instrument", state.get("company_of_interest", "EURUSD"))
# Automatically adapts to analyze: EURUSD, GBPJPY, AUDUSD, USDJPY, etc.
```

**Currency Pair Context:**
The researcher receives a dynamically generated context explaining:
- Base currency (bought) vs. Quote currency (sold)
- Interest rate differential implications
- How rates affect pair direction

Example for EURUSD:
```
You are analyzing the currency pair EURUSD, where:
- Base Currency: EUR (the currency being bought/sold)
- Quote Currency: USD (the pricing currency)
- A rise in EURUSD means EUR is strengthening relative to USD
- Analyze both EUR and USD macro conditions, interest rates, and economic outlooks
- Compare interest rate differentials: (EUR rates - USD rates)
- Higher interest rate differential favors buying EURUSD
```

**Bullish Case Keywords:**
- ✅ Favorable interest rate differentials favoring the base currency
- ✅ Stronger economic growth or lower inflation in base currency country
- ✅ Policy divergence (base currency tightening, quote loosening)
- ✅ Positive technical signals (uptrends, oversold bounces, breakouts)
- ✅ Bullish sentiment and positioning from traders
- ✅ Recent positive news or central bank hawkish signals

**Output:**
A persuasive argument that:
1. Uses Phase 1 data as evidence
2. Addresses potential bear counterpoints
3. Engages in conversational debate style
4. Updates the conversation history and state

---

### 2. Bear Researcher

**File:** `tradingagents/agents/researchers/bear_researcher.py`

**Purpose:** Build a compelling bearish case against the currency pair (or for shorting)

**Inputs from Phase 1:**
- `state["market_report"]` - Technical analysis
- `state["sentiment_report"]` - Trader sentiment and positioning
- `state["news_report"]` - Recent events
- `state["macro_report"]` - Macroeconomic analysis

**Dynamic Currency Pair Support:**
```python
currency_pair = state.get("instrument", state.get("company_of_interest", "EURUSD"))
# Same dynamic support as Bulls - works with any currency pair
```

**Bearish Case Keywords:**
- ❌ Unfavorable interest rate differentials (quote currency higher)
- ❌ Weaker economic growth or rising inflation in base currency country
- ❌ Policy divergence (quote currency tightening, base loosening)
- ❌ Negative technical signals (downtrends, resistance rejection, breakdowns)
- ❌ Bearish sentiment or extreme positioning from retailers
- ❌ Recent negative news or central bank dovish signals
- ❌ Geopolitical risks affecting the base currency

**Output:**
A persuasive counter-argument that:
1. Challenges the bull's assumptions
2. Presents bearish evidence from Phase 1
3. Engages in debate format
4. Updates conversation history

---

## Key Differences: Phase 1 vs Phase 2

| Aspect | Phase 1 (Analysts) | Phase 2 (Researchers) |
|--------|-------------------|----------------------|
| **Role** | Gather & report data | Debate & synthesize |
| **Input** | Raw market data | Phase 1 reports |
| **Output** | Objective reports | Subjective arguments |
| **Process** | Sequential analysis | Iterative debate |
| **Memory** | None | Learns from past debates |
| **Goal** | Present facts | Build persuasive case |

---

## Phase 2 State Flow

### Initial State (from Phase 1):
```python
state = {
    "instrument": "EURUSD",  # Currency pair to analyze
    "market_report": "...",  # From Market Analyst
    "sentiment_report": "...",  # From Social Media Analyst
    "news_report": "...",  # From News Analyst
    "macro_report": "...",  # From Macro Analyst
    "investment_debate_state": {
        "history": "",  # Conversation history
        "bull_history": "",  # Bull's positions only
        "bear_history": "",  # Bear's positions only
        "current_response": "",  # Last argument
        "count": 0  # Number of turns
    }
}
```

### After Bull Turn:
```python
state["investment_debate_state"] = {
    "history": "Bull Analyst: [bullish argument]\n",
    "bull_history": "Bull Analyst: [bullish argument]\n",
    "bear_history": "",
    "current_response": "Bull Analyst: [bullish argument]",
    "count": 1
}
```

### After Bear Turn:
```python
state["investment_debate_state"] = {
    "history": "Bull Analyst: [bullish arg]\nBear Analyst: [bearish counter]\n",
    "bull_history": "Bull Analyst: [bullish arg]\n",
    "bear_history": "Bear Analyst: [bearish counter]\n",
    "current_response": "Bear Analyst: [bearish counter]",
    "count": 2
}
```

---

## Memory System in Phase 2

Both Bull and Bear researchers use **FinancialSituationMemory** to store lessons from past debates:

```python
past_memories = memory.get_memories(curr_situation, n_matches=2)
# Returns: Previous similar situations and what worked/didn't work
```

**Example Memory Entry:**
```
{
    "situation": "EURUSD with ECB easing + Fed holding rates",
    "recommendation": "Bearish case won - EUR weakness was correct",
    "lesson": "When central banks diverge in policy, 
              the easing bank's currency tends to weaken"
}
```

This allows researchers to:
- ✅ Learn from historical patterns
- ✅ Avoid repeating failed arguments
- ✅ Reference past successes
- ✅ Refine debate strategy over time

---

## Phase 2 Execution Flow

### Example: EURUSD Analysis

**Given State from Phase 1:**
```
market_report: "EUR in downtrend, below 200 SMA, RSI oversold at 30"
sentiment_report: "Bearish positioning by retail traders, 70% short"
news_report: "ECB signals potential rate cuts coming"
macro_report: "USD rate at 5.25%, EUR rate at 4.25%; Fed hawkish, ECB dovish"
```

**Bull Researcher Argument:**
```
"EUR is oversold on the technical, presenting a bounce opportunity. 
The macro backdrop shows a clear rate differential favoring USD, 
but the recent ECB hawkish surprise could re-value EUR higher. 
We've seen this pattern before—excessive retail shorts often reverse."
```

**Bear Researcher Counter:**
```
"The oversold bounce is a false hope in a downtrend. 
The macro fundamentals remain bearish: ECB easing while Fed holds steady 
creates a powerful 100bps rate differential against EUR. 
Historical precedent shows rate divergence drives sustained weakness."
```

**Debate Continues Until:**
- Consensus reached (e.g., "Slight bearish bias, avoid longs")
- Maximum turns reached
- Research Manager called for synthesis

---

## Integration with Phase 1

### Required Phase 1 Reports:

**1. Market Report** (from Forex Market Analyst):
```
TECHNICAL ANALYSIS - EURUSD
Trend: Downtrend (200 SMA at 1.1050, price at 1.0950)
RSI: 35 (oversold)
MACD: Bearish
Support: 1.0900, Resistance: 1.1100
```

**2. Sentiment Report** (from Social Media Analyst):
```
TRADER POSITIONING - EURUSD
Retail: 70% short
Sentiment: Bearish
CoT Data: Large specs heavily short
```

**3. News Report** (from News Analyst):
```
RECENT EVENTS - EURUSD
- ECB signals Q2 rate cuts possible
- Fed holds rates steady
- Geopolitical tensions: Moderate risk
```

**4. Macro Report** (from Macro Analyst):
```
MACROECONOMIC ANALYSIS - EURUSD
- EUR Rate: 4.25% (ECB on hold)
- USD Rate: 5.25% (Fed holding steady)
- Rate Differential: 100 bps favoring USD
- ECB Policy: Easing likely
- Fed Policy: Restrictive, higher for longer
- Policy Divergence: EUR weakness expected
```

---

## Forex-Specific Debate Topics

Phase 2 researchers focus on **forex-specific themes** not found in stock debates:

### 1. Interest Rate Differentials
```python
# Bull perspective:
"If USD-EUR differential narrows (EUR rates rise), EUR strengthens"

# Bear perspective:
"Widening differential (EUR rates fall) pushes EUR down"
```

### 2. Carry Trade Dynamics
```python
# Bull perspective:
"High interest rate differential makes EUR/USD a profitable carry trade"

# Bear perspective:
"Negative carry (EUR lower rate) makes it a loss-making trade"
```

### 3. Policy Divergence
```python
# Bull perspective:
"Fed pausing while ECB eases = potential USD strength reversal"

# Bear perspective:
"ECB easing while Fed holds = sustained EUR weakness"
```

### 4. Central Bank Forward Guidance
```python
# Bull perspective:
"ECB's hawkish surprise could re-value EUR higher vs expectations"

# Bear perspective:
"Fed signals 'higher for longer' = USD strength sustained"
```

### 5. Safe-Haven Flows
```python
# Bull perspective:
"Geopolitical risk favors safe-haven USD demand"

# Bear perspective:
"Risk-off sentiment benefits JPY over other pairs"
```

---

## Configuration for Phase 2

### In `setup.py`:

```python
# Create Bull Researcher
bull_researcher = create_bull_researcher(
    llm=self.quick_thinking_llm,
    memory=self.bull_memory
)

# Create Bear Researcher
bear_researcher = create_bear_researcher(
    llm=self.quick_thinking_llm,
    memory=self.bear_memory
)

# Add to graph
graph.add_node("bull_researcher", bull_researcher)
graph.add_node("bear_researcher", bear_researcher)
```

### State Requirements:

The graph state must include:
```python
state = {
    # From Phase 1
    "instrument": str,  # Currency pair code (e.g., "EURUSD")
    "company_of_interest": str,  # Fallback for currency pair
    "market_report": str,  # Forex technical analysis
    "sentiment_report": str,  # Trader sentiment data
    "news_report": str,  # Recent news and events
    "macro_report": str,  # Macro analysis report
    
    # For Phase 2
    "investment_debate_state": {
        "history": str,
        "bull_history": str,
        "bear_history": str,
        "current_response": str,
        "count": int
    }
}
```

---

## Output: Phase 2 Debate Example

### Bull Analyst Turn 1:
```
Bull Analyst: The EUR/USD pair presents a compelling buying opportunity. 
From a technical perspective, we're seeing an oversold condition with RSI at 30, 
which historically precedes reversals. More importantly, the macro backdrop 
shows clear support:

1. The 100bp interest rate differential is pricing in a lot of bearishness
2. ECB forward guidance hints at a potential shift toward easing caution
3. Historical precedent: When technicals are this oversold AND macro provides 
   a reason for reversal, we typically see strong counter-trend moves

A long position at current levels offers a favorable risk/reward.
```

### Bear Analyst Turn 1:
```
Bear Analyst: The bull makes a classic error—confusing oversold technicals 
with a reversal catalyst. Let me counter:

1. Oversold bounces in downtrends are often faked; the 200 SMA at 1.1050 
   provides strong resistance
2. The 100bp rate differential isn't "priced in"—it's the DRIVER of sustained 
   weakness. ECB easing while Fed holds creates divergence momentum
3. Historical precedent actually supports mean reversion downward, not upward

The path of least resistance remains DOWN. We're shorting into strength, not
buying into weakness.
```

### Bull Analyst Turn 2:
```
Bull Analyst: The bear ignores the reflexivity in the system. Let me explain:

1. The rate differential you cite creates INCENTIVE for rate convergence
2. If ECB actually hikes its forward guidance (likely next meeting), the 
   differential collapses and EUR reverses in classic fashion
3. We're not buying THE OVERSOLD BOUNCE—we're buying POLICY CHANGE precedent

Historical precedent when central banks reverse course: Sharp rallies in 
devalued currency. This is equivalent.
```

---

## Validating Phase 2 Implementation

### ✅ Correct Implementation Checklist:

- [x] Researchers read Phase 1 reports from state (not calling tools directly)
- [x] Dynamic currency pair support (reads from state["instrument"])
- [x] Pair context builder included (explains dual-currency dynamics)
- [x] Debate-focused prompts (discusses, argues, refutes)
- [x] Memory integration (learns from past debates)
- [x] Forex-specific language (trading, not investing; carry, not dividends)
- [x] Both analysts receive the same Phase 1 data
- [x] Output updates conversation history properly

---

## Next: Phase 3

Once Phase 2 debate concludes (typically 2-4 turns), the pipeline moves to:

**Phase 3: Trading Decision**
- Research Manager synthesizes debate into final recommendation
- Trader determines position sizing and leverage
- Execution logic applies forex-specific rules (stop-loss, take-profit)
- Risk management applies (max position size, max daily loss)

---

## Summary

**Phase 2** transforms Phase 1's objective data into subjective, debated trade theses. 

**Key Features:**
1. ✅ Receives all Phase 1 analyst outputs
2. ✅ Dynamically supports any currency pair
3. ✅ Debates bearish vs bullish cases
4. ✅ Learns from historical precedent via memory
5. ✅ Produces conversation history for Research Manager
6. ✅ Focuses on forex-specific debate topics (rates, divergence, carry)

**Success Metrics:**
- Phase 1 data is properly synthesized
- Arguments are specific and evidence-based
- Both sides engage in true debate (not monologues)
- Memory improves argument quality over time
- Output is ready for Phase 3 trader decision


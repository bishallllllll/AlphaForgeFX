# Phase 3 Integration Guide - Adding Trader to TradingGraph

**Purpose**: Step-by-step instructions to integrate Phase 3 Trader into the existing `TradingAgentsGraph`

---

## Overview

The Phase 3 Trader node needs to be integrated into the existing LangGraph workflow. This guide provides exact code snippets and locations for integration.

---

## Integration Steps

### Step 1: Update Imports in `trading_graph.py`

**File**: `tradingagents/graph/trading_graph.py`

**Add to imports section**:
```python
from tradingagents.agents import create_forex_trader  # ADD THIS LINE
```

**Location**: Around line 15-25 with other agent imports

---

### Step 2: Instantiate Trader in `TradingAgentsGraph.__init__()`

**File**: `tradingagents/graph/trading_graph.py`

**Location**: In the `__init__` method after other agent initialization

**Current code structure** (example):
```python
def __init__(self, selected_analysts=["market", "social", "news", "fundamentals"], ...):
    # ... existing initialization code ...
    
    # Create agents
    self.market_analyst = create_market_analyst(self.llm)
    self.news_analyst = create_news_analyst(self.llm)
    # ... other analysts ...
```

**Add after other traders** (if any):
```python
    # Phase 3: Trader Decision Node
    self.trader = create_forex_trader(
        llm=self.llm,
        memory=self.memory
    )
```

---

### Step 3: Add Trader Node to Graph

**File**: `tradingagents/graph/trading_graph.py`

**Location**: In the method where nodes are added (typically init method)

**Pattern** (add alongside other nodes):
```python
        # Add existing nodes
        self.graph.add_node("MarketAnalyst", self.market_analyst)
        self.graph.add_node("NewsAnalyst", self.news_analyst)
        # ... other nodes ...
        
        # ADD THIS - Phase 3 Trader Node
        self.graph.add_node("Trader", self.trader)
```

---

### Step 4: Connect Graph Edges

**File**: `tradingagents/graph/trading_graph.py`

The trader should receive input from the Phase 2 debate (bull/bear research).

**Determine the current Phase 2 flow**:
- If there's a "Research Manager" or "Judge" node after bull/bear debate, connect from there
- Otherwise, connect from the end of the debate loop

**Add edges** (example - adjust based on your actual graph structure):

```python
        # Phase 2 → Phase 3 Transition
        # From the last researcher/judge → Trader
        self.graph.add_edge("DebateEnd", "Trader")  # or your actual end node
        
        # Phase 3 → Phase 4 Transition (optional, if risk management exists)
        # self.graph.add_edge("Trader", "RiskManagement")
        # Otherwise, Trader might be terminal node for now
        self.graph.add_edge("Trader", END)
```

---

### Step 5: Update Conditional Logic (if needed)

**File**: `tradingagents/graph/conditional_logic.py`

If your graph has conditional routing, update to route to trader at the right point:

```python
def route_after_research_debate(state):
    """Route from Phase 2 debate to Phase 3 trader"""
    debate_state = state.get("investment_debate_state", {})
    
    # Check if debate has completed minimum rounds
    rounds = debate_state.get("count", 0)
    if rounds >= 2:  # Minimum 2 rounds of debate
        return "Trader"
    else:
        # Return to debate
        return "BullResearcher"
```

---

### Step 6: Ensure State Initialization

**File**: `tradingagents/graph/trading_graph.py` (in graph initialization)

Ensure Phase 1 reports are available in state before trader is called:

```python
# When initializing state, include:
state = {
    "company_of_interest": currency_pair,  # e.g., "EURUSD"
    "instrument": currency_pair,            # Phase 3 uses this
    "market_report": market_analyst_output,
    "sentiment_report": sentiment_analyst_output,
    "news_report": news_analyst_output,
    "macro_report": macro_analyst_output,
    "investment_debate_state": debate_state,
    # ... other fields ...
}
```

---

## Complete Integration Example

### Minimal Graph Structure with Phase 3

```python
from langgraph.graph import StateGraph, START, END

class TradingAgentsGraph:
    def __init__(self, llm, memory):
        self.llm = llm
        self.memory = memory
        
        # Create agents
        self.bull_researcher = create_bull_researcher(llm, memory)
        self.bear_researcher = create_bear_researcher(llm, memory)
        self.trader = create_forex_trader(llm, memory)  # ← Phase 3 Trader
        
        # Build graph
        self.graph = StateGraph(AgentState)
        
        # Add nodes
        self.graph.add_node("BullResearcher", self.bull_researcher)
        self.graph.add_node("BearResearcher", self.bear_researcher)
        self.graph.add_node("Trader", self.trader)  # ← Add trader node
        
        # Add edges
        self.graph.add_edge(START, "BullResearcher")
        self.graph.add_edge("BullResearcher", "BearResearcher")
        self.graph.add_edge("BearResearcher", "BullResearcher")  # Debate loop
        
        # Conditional: exit debate → go to trader
        # (Implement in conditional_logic.py)
        self.graph.add_conditional_edges(
            "BearResearcher",
            self._decide_continue_debate_or_trade
        )
        
        self.graph.add_edge("Trader", END)  # ← Trader leads to end (or Phase 4)
        
        self.compiled_graph = self.graph.compile()
    
    def _decide_continue_debate_or_trade(self, state):
        rounds = state.get("investment_debate_state", {}).get("count", 0)
        if rounds >= 4:  # Min 4 rounds
            return "Trader"
        else:
            return "BullResearcher"  # More debate
```

---

## What Happens When Trader Runs

### Input State (from Phase 2)
```python
{
    "instrument": "EURUSD",
    "investment_debate_state": {
        "history": "Bull Analyst: ... Bear Analyst: ... Bull Analyst: ...",
        "bull_history": "Bull Analyst: ...",
        "bear_history": "Bear Analyst: ...",
        "count": 4
    },
    "market_report": "Technical Analysis: ...",
    "sentiment_report": "Sentiment Data: ...",
    "news_report": "News Events: ...",
    "macro_report": "Economic Indicators: ...",
    # ... other state fields ...
}
```

### Trader Processing
1. Extracts debate history
2. Retrieves Phase 1 reports
3. Gets similar past trades from memory
4. Calls LLM with comprehensive prompt
5. Parses response for trading parameters
6. Extracts structured decision

### Output State (Updated)
```python
{
    # All input fields preserved, plus:
    "trader_decision": "Full analysis including entry, SL, TP...",
    "trading_signal": "BUY",
    "entry_level": 1.0850,
    "stop_loss": 1.0800,
    "take_profit_1": 1.0920,
    "take_profit_2": 1.0980,
    "conviction_level": 75,
    "risk_reward_ratio": 2.0,
    "position_size": "2% of account",
    "sender": "Trader",
    "messages": [AIMessage(...)]  # For audit trail
}
```

---

## Testing Integration

### Quick Validation Test

```python
from tradingagents.graph import TradingAgentsGraph

# Initialize
graph = TradingAgentsGraph(llm=your_llm, memory=your_memory)

# Test with sample state
test_state = {
    "instruction": "Trade EURUSD",
    "instrument": "EURUSD",
    "company_of_interest": "EURUSD",
    "investment_debate_state": {
        "history": "Bull Analyst: Strong bullish case...\nBear Analyst: Weak bearish case...",
        "bull_history": "Bull Analyst: ...",
        "bear_history": "Bear Analyst: ...",
        "count": 3
    },
    "market_report": "Technical: Bullish on hourly, daily bullish",
    "sentiment_report": "Social: 70% long positioning",
    "news_report": "Positive economic data release",
    "macro_report": "Fed likely to cut rates",
}

# Run just the trader
output = graph.trader(test_state)
print(output["trading_signal"])  # Should print trading signal
print(output["entry_level"])     # Should print entry price
print(output["risk_reward_ratio"])  # Should print RR ratio
```

---

## Troubleshooting

### Issue: Trader not receiving debate state
**Solution**: Ensure `investment_debate_state` is properly initialized and populated in state before trader is called

### Issue: Price levels showing as None
**Solution**: 
- Verify LLM response contains price levels in format like "Entry: 1.0850"
- Update regex patterns in `_parse_trader_response()` if LLM uses different format

### Issue: State fields not persisting
**Solution**: Ensure trader returns all necessary fields in its output dictionary

### Issue: No entry/stop/profit validation
**Current**: None exists (enhancement to add)  
**Temporary fix**: Add validation in conditional_logic.py before advancing to Phase 4

---

## Next Steps

1. ✅ Phase 3 Trader implemented (`forex_trader.py`)
2. ✅ State fields updated (`agent_states.py`)
3. ⏳ Integration into graph (THIS GUIDE)
4. ⏳ Testing & validation
5. ⏳ Phase 4 Risk Management (if needed)

---

## API Reference

### create_forex_trader(llm, memory)

**Parameters**:
- `llm`: LLM client (create_openai_client, create_anthropic_client, etc.)
- `memory`: FinancialSituationMemory instance for pattern learning

**Returns**: 
- Callable node function that accepts state dict and returns updated state dict

**Node Function Signature**:
```python
def forex_trader_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Returns updated state with trader_decision, trading_signal, etc.
    return {...}
```

---


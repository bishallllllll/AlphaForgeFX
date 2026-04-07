"""
Phase 3: Trader Decision Engine for Forex Trading

This module synthesizes the Phase 2 bull/bear research debate and Phase 1 analyst reports
to generate structured trading decisions with entry points, stop loss, take profit, and
position sizing recommendations.

The trader acts as a decision-making agent that:
1. Analyzes debate quality and conviction strength
2. Reviews technical levels from Phase 1 analysis
3. Evaluates sentiment and macro context
4. Generates actionable trading signals with risk management parameters
"""

import json
import re
from typing import Dict, Any, Optional


def create_forex_trader(llm, memory):
    """
    Create a trader node for Phase 3 decision-making.
    
    Args:
        llm: Language model client for analysis
        memory: Memory system for past trading decisions
        
    Returns:
        A function that processes state and generates trading decisions
    """
    
    def forex_trader_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Phase 2 debate and generate trading decision.
        
        Inputs from state:
        - investment_debate_state: Bull vs Bear research debate
        - market_report: Phase 1 technical analysis
        - sentiment_report: Phase 1 trader sentiment
        - news_report: Phase 1 news analysis
        - macro_report: Phase 1 macroeconomic analysis
        - instrument (or company_of_interest): Currency pair (e.g., EURUSD)
        
        Returns:
        - trader_decision: Structured decision with all trading parameters
        - trading_signal: Signal strength (Strong Buy/Buy/Hold/Sell/Strong Sell)
        - entry_level: Recommended entry price
        - stop_loss: Stop loss level
        - take_profit_1: First take profit level (50% position)
        - take_profit_2: Second take profit level (remaining 50%)
        - position_size: Recommended position size
        - risk_reward_ratio: Risk to reward ratio
        """
        
        # Extract Phase 2 debate data
        investment_debate_state = state.get("investment_debate_state", {})
        debate_history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")
        bear_history = investment_debate_state.get("bear_history", "")
        
        # Extract Phase 1 analyst reports
        market_report = state.get("market_report", "")
        sentiment_report = state.get("sentiment_report", "")
        news_report = state.get("news_report", "")
        macro_report = state.get("macro_report", "")
        
        # Get currency pair
        currency_pair = state.get("instrument", state.get("company_of_interest", "EURUSD"))
        
        # Retrieve past trading memories for pattern recognition
        curr_situation = f"{market_report}\n\n{sentiment_report}\n\n{news_report}\n\n{macro_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=3)
        
        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += f"Trade {i}: {rec.get('recommendation', '')}\n\n"
        else:
            past_memory_str = "No similar past trading situations found."
        
        # Construct the trader prompt
        prompt = f"""You are an expert Forex Trader synthesizing research from Phase 2 analyst debate to make a trading decision on {currency_pair}.

## DEBATE ANALYSIS
Your job is to evaluate the quality and conviction of the bull and bear cases presented by the research team.

Bull Analyst Arguments:
{bull_history}

Bear Analyst Arguments:
{bear_history}

Debate Summary:
{debate_history}

## SUPPORTING RESEARCH (Phase 1)

Technical Analysis (Market Technician):
{market_report}

Trader Sentiment Analysis:
{sentiment_report}

News & Events Analysis:
{news_report}

Macroeconomic Analysis:
{macro_report}

## PAST TRADING PATTERNS
Learning from similar market situations:
{past_memory_str}

## YOUR TASK

Based on this comprehensive analysis, provide a structured trading decision for {currency_pair}. Your response MUST include:

1. **Debate Verdict**: Which case (bull/bear) was more compelling and why? Score each side 1-10.

2. **Market Bias**: Determine the primary trading bias:
   - Strong Buy (Very bullish, clear technical + fundamental support)
   - Buy (Moderately bullish)
   - Hold (Neutral, waiting for clarity)
   - Sell (Moderately bearish)
   - Strong Sell (Very bearish, clear technical + fundamental weakness)

3. **Conviction Level**: Rate your confidence 0-100% (based on debate quality, alignment of multiple timeframes, sentiment confirmation, macro support).

4. **Entry Strategy**:
   - Primary entry point (specific price level)
   - Entry rationale (which technical level? why now?)
   - Alternative entry if price moves

5. **Risk Management**:
   - Stop loss placement (specific level)
   - Stop loss rationale (invalidation of thesis)
   - Position size recommendation (% of account at risk)
   - Initial risk per pip/point

6. **Profit Taking**:
   - First target (TP1) - where to take 50% profits
   - Second target (TP2) - where to take remaining 50% at risk
   - Trailing stop consideration if trend continues

7. **Risk/Reward Analysis**:
   - Calculate Risk = (Entry Level - Stop Loss)
   - Calculate Reward = (TP2 - Entry Level)
   - Risk/Reward Ratio (should be at least 1:1.5 for a good trade)

8. **Timeframe Alignment**: Are technicals, sentiment, news, and macro all pointing the same direction?

9. **Lesson Application**: How do past trading patterns inform this decision? What worked before?

10. **Final Recommendation**: One-sentence summary of your decision.

## RESPONSE FORMAT

Please structure your response with clear headers for each section. Include specific price levels (not ranges), clear reasoning, and actionable details. The response should be detailed enough that another trader could execute the trade based on your recommendation.

For example:
- Entry: 1.0850 (reason: support test from macro support level)
- SL: 1.0800 (reason: below recent low)
- TP1: 1.0920 (reason: previous resistance)
- TP2: 1.0980 (reason: structural resistance)
- RR: 2.0
"""

        # Get trader analysis from LLM
        result = llm.invoke(prompt)
        trader_analysis = result.content
        
        # Extract structured trading decision
        structured_decision = _parse_trader_response(trader_analysis, currency_pair)
        
        # Return updated state with trading decision
        return {
            "trader_decision": trader_analysis,
            "trading_signal": structured_decision.get("signal", "HOLD"),
            "entry_level": structured_decision.get("entry", None),
            "stop_loss": structured_decision.get("stop_loss", None),
            "take_profit_1": structured_decision.get("tp1", None),
            "take_profit_2": structured_decision.get("tp2", None),
            "conviction_level": structured_decision.get("conviction", 0),
            "risk_reward_ratio": structured_decision.get("risk_reward", 0),
            "position_size": structured_decision.get("position_size", "To be determined"),
            "messages": [result],
            "sender": "Trader",
        }
    
    return forex_trader_node


def _parse_trader_response(response: str, currency_pair: str) -> Dict[str, Any]:
    """
    Parse trader response to extract structured trading parameters.
    
    Args:
        response: Raw trader analysis text
        currency_pair: Currency pair being traded (e.g., EURUSD)
        
    Returns:
        Dictionary with extracted trading parameters
    """
    result = {
        "signal": "HOLD",
        "entry": None,
        "stop_loss": None,
        "tp1": None,
        "tp2": None,
        "conviction": 0,
        "risk_reward": 0,
        "position_size": "To be determined",
    }
    
    # Extract signal
    signal_patterns = {
        r"strong\s+buy": "STRONG_BUY",
        r"strong buy": "STRONG_BUY",
        r"^buy\b": "BUY",
        r"\bhold\b": "HOLD",
        r"^sell\b": "SELL",
        r"strong\s+sell": "STRONG_SELL",
        r"strong sell": "STRONG_SELL",
    }
    
    response_lower = response.lower()
    for pattern, signal in signal_patterns.items():
        if re.search(pattern, response_lower):
            result["signal"] = signal
            break
    
    # Extract conviction level (0-100%)
    conviction_match = re.search(r'conviction\s*(?:level)?[:\s]*(\d+)\s*%', response, re.IGNORECASE)
    if conviction_match:
        result["conviction"] = int(conviction_match.group(1))
    
    # Extract entry level (assuming format like "Entry: 1.0850")
    entry_match = re.search(r'(?:primary\s+)?entry[:\s]*(\d+\.\d+)', response, re.IGNORECASE)
    if entry_match:
        result["entry"] = float(entry_match.group(1))
    
    # Extract stop loss level
    sl_match = re.search(r'(?:stop\s+loss|SL)[:\s]*(\d+\.\d+)', response, re.IGNORECASE)
    if sl_match:
        result["stop_loss"] = float(sl_match.group(1))
    
    # Extract TP1 (first take profit)
    tp1_match = re.search(r'(?:tp1|first\s+target|take\s+profit\s+1)[:\s]*(\d+\.\d+)', response, re.IGNORECASE)
    if tp1_match:
        result["tp1"] = float(tp1_match.group(1))
    
    # Extract TP2 (second take profit)
    tp2_match = re.search(r'(?:tp2|second\s+target|take\s+profit\s+2)[:\s]*(\d+\.\d+)', response, re.IGNORECASE)
    if tp2_match:
        result["tp2"] = float(tp2_match.group(1))
    
    # Extract risk/reward ratio
    rr_match = re.search(r'risk[:/\s]+reward[:\s]*(\d+[.]\d+|\d+)', response, re.IGNORECASE)
    if rr_match:
        result["risk_reward"] = float(rr_match.group(1))
    
    # Extract position size if mentioned
    pos_match = re.search(r'position\s+size[:\s]*([^.\n]+)', response, re.IGNORECASE)
    if pos_match:
        result["position_size"] = pos_match.group(1).strip()
    
    return result

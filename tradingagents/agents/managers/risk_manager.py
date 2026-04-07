"""
Phase 4: Risk Manager - Synthesizing Trader Decision with Risk Debate

This module creates the Risk Manager node that:
1. Takes the Phase 3 Trader Decision (specific entry/exit/SL/TP levels)
2. Evaluates it through three risk perspectives (Aggressive/Conservative/Neutral debate)
3. Synthesizes into a final risk-adjusted trading decision
4. Potentially adjusts position size, entry, or exit based on risk assessment
"""

from typing import Dict, Any


def create_risk_manager(llm, memory):
    """
    Create a risk manager node for Phase 4.
    
    Takes the Phase 3 trader decision and synthesizes the risk team debate
    to produce a final risk-adjusted trading decision.
    
    Args:
        llm: Language model client
        memory: Memory system for past decisions
        
    Returns:
        A function that processes state and generates final trading decision
    """
    
    def risk_manager_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize risk debate and produce final trading decision.
        
        Takes Phase 3 trader decision and evaluates it through:
        - Aggressive perspective (maximize reward, accept higher risk)
        - Conservative perspective (minimize loss, protect capital)
        - Neutral perspective (balanced approach)
        
        Returns:
        - final_risk_decision: Comprehensive risk analysis and final decision
        - risk_adjusted_signal: Modified signal (may differ from trader signal)
        - position_size_adjusted: Adjusted position size based on risk
        - final_entry: Final entry level (may differ from trader entry)
        - final_exit: Final exit level
        """
        
        # Extract risk debate data
        risk_debate_state = state.get("risk_debate_state", {})
        debate_history = risk_debate_state.get("history", "")
        aggressive_history = risk_debate_state.get("aggressive_history", "")
        conservative_history = risk_debate_state.get("conservative_history", "")
        neutral_history = risk_debate_state.get("neutral_history", "")
        
        # Extract Phase 3 trader decision
        trader_decision = state.get("trader_decision", "")
        trading_signal = state.get("trading_signal", "HOLD")
        entry_level = state.get("entry_level", None)
        stop_loss = state.get("stop_loss", None)
        take_profit_1 = state.get("take_profit_1", None)
        take_profit_2 = state.get("take_profit_2", None)
        conviction_level = state.get("conviction_level", 0)
        risk_reward_ratio = state.get("risk_reward_ratio", 0)
        position_size = state.get("position_size", "")
        
        # Extract Phase 1 & 2 reports
        market_report = state.get("market_report", "")
        sentiment_report = state.get("sentiment_report", "")
        news_report = state.get("news_report", "")
        macro_report = state.get("macro_report", "")
        
        # Get currency pair
        currency_pair = state.get("instrument", state.get("company_of_interest", "EURUSD"))
        
        # Retrieve past trading memories
        curr_situation = f"{market_report}\n\n{sentiment_report}\n\n{news_report}\n\n{macro_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=3)
        
        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += f"Past Trade {i}: {rec.get('recommendation', '')}\n\n"
        else:
            past_memory_str = "No similar past risk assessments found."
        
        # Construct the risk manager prompt
        prompt = f"""You are the Risk Manager synthesizing the risk team's debate to produce a final risk-adjusted trading decision.

## PHASE 3 TRADER DECISION (Awaiting Risk Assessment)

Trader's Analysis: {trader_decision}

Proposed Signal: {trading_signal}
Entry Level: {entry_level}
Stop Loss: {stop_loss}
TP1: {take_profit_1}
TP2: {take_profit_2}
Conviction: {conviction_level}%
Risk/Reward: {risk_reward_ratio}
Position Size: {position_size}

## PHASE 4 RISK TEAM DEBATE

The following three risk perspectives have evaluated the trader's decision:

**Aggressive Perspective** (Maximize Reward, Accept Risk):
{aggressive_history}

**Conservative Perspective** (Minimize Loss, Protect Capital):
{conservative_history}

**Neutral Perspective** (Balanced Risk/Reward):
{neutral_history}

### Full Debate History:
{debate_history}

## SUPPORTING DATA

Technical Analysis: {market_report}
Sentiment Data: {sentiment_report}
News & Events: {news_report}
Macro Context: {macro_report}

## PAST TRADING PATTERNS

Learning from similar situations where risk assessment was critical:
{past_memory_str}

## YOUR TASK - SYNTHESIZE INTO FINAL DECISION

Based on the risk team debate, produce a comprehensive final trading decision for {currency_pair}. Your response MUST include:

### 1. Risk Assessment Summary
- Score each perspective (Aggressive/Conservative/Neutral) on convincingness (1-10)
- Determine which perspective(s) have the strongest risk-based reasoning
- Identify critical risk factors the traders debated

### 2. Decision Validation
- Is the trader's decision sound from a risk perspective?
- Are entry/stop/profit levels appropriate for current volatility?
- Is position size reasonable given account constraints?
- Does the risk/reward ratio meet minimum thresholds (1.5:1)?

### 3. Potential Risk Adjustments
Choose ONE of the following:
a) **APPROVE**: Trader decision is sound, proceed with proposed levels
b) **APPROVE WITH ADJUSTMENTS**: Accept signal but modify:
   - Reduce position size (too aggressive for volatility)
   - Tighten stop loss (reduce risk exposure)
   - Move profit targets (lock gains earlier)
   - Require additional confirmation before entry
c) **REJECT**: Trader decision fails risk criteria
   - Why does it violate risk principles?
   - What would make it acceptable?

### 4. Final Risk-Adjusted Decision
Provide SPECIFIC LEVELS (numbers, not ranges):
- Final Signal: (Accept Trader's signal or propose alternative)
- Final Entry: (Accept {entry_level} or propose adjusted level)
- Final Stop Loss: (Accept {stop_loss} or tighten/loosen)
- Final Position Size: (Accept {position_size} or adjust)
- Reason for any changes

### 5. Risk Metrics Validation
- Calculate Risk: (Final Entry - Final Stop Loss) = ___ pips
- Calculate Reward: (Final Exit - Final Entry) = ___ pips
- Final Risk/Reward: ___ (must be ≥1.5)
- Volatility Adjustment: (Consider ATR or volatility context)

### 6. Lesson Application
How do past trading patterns inform this risk decision? What worked/failed before in similar situations?

### 7. Trader Execution Checklist
- ✓ Entry price confirmed
- ✓ Stop loss is below/above recent extremes (invalid if broken)
- ✓ Profit targets identified with 50/50 exit strategy
- ✓ Position size appropriate for account size/risk tolerance
- ✓ Risk/reward ratio acceptable
- ✓ Macro/sentiment/technical aligned
- ✓ Ready for execution

### 8. Final Recommendation (One Sentence)
Decisive conclusion: Approve trader decision, approve with adjustments, or reject with modifications.

## RESPONSE FORMAT

Structure your response with clear headers for each section. Be specific with numbers (prices, percentages, pips). Your synthesis should balance the three perspectives while maintaining focus on capital preservation and acceptable risk metrics. The goal is not to go ultra-conservative or ultra-aggressive, but to synthesize a prudent, balanced final decision.

Remember: The best risk management acknowledges both the potential for profits AND protects against catastrophic losses.
"""

        # Get risk manager analysis from LLM
        result = llm.invoke(prompt)
        risk_analysis = result.content
        
        # Extract final decision parameters
        final_decision = _parse_risk_manager_response(risk_analysis, entry_level, stop_loss, position_size)
        
        # Return updated state
        return {
            "final_risk_decision": risk_analysis,
            "risk_adjusted_signal": final_decision.get("signal", trading_signal),
            "final_entry": final_decision.get("entry", entry_level),
            "final_stop_loss": final_decision.get("stop_loss", stop_loss),
            "final_position_size": final_decision.get("position_size", position_size),
            "adjustment_reason": final_decision.get("reason", ""),
            "risk_approval_status": final_decision.get("approval", "PENDING"),
            "messages": [result],
            "sender": "RiskManager",
        }
    
    return risk_manager_node


def _parse_risk_manager_response(response: str, original_entry: float, original_sl: float, original_size: str) -> Dict[str, Any]:
    """
    Parse risk manager response to extract final adjusted parameters.
    
    Args:
        response: Raw risk manager analysis text
        original_entry: Original trader entry level
        original_sl: Original trader stop loss
        original_size: Original position size recommendation
        
    Returns:
        Dictionary with final adjusted parameters
    """
    import re
    
    result = {
        "signal": "HOLD",
        "entry": original_entry,
        "stop_loss": original_sl,
        "position_size": original_size,
        "approval": "PENDING",
        "reason": "",
    }
    
    response_lower = response.lower()
    
    # Determine approval status
    if "approve with adjustments" in response_lower or "adjust" in response_lower:
        result["approval"] = "APPROVED_WITH_ADJUSTMENTS"
    elif "approve" in response_lower and "reject" not in response_lower:
        result["approval"] = "APPROVED"
    elif "reject" in response_lower:
        result["approval"] = "REJECTED"
    
    # Extract final signal
    signal_patterns = {
        r"final\s+signal[:\s]*strong\s+buy": "STRONG_BUY",
        r"final\s+signal[:\s]*buy": "BUY",
        r"final\s+signal[:\s]*hold": "HOLD",
        r"final\s+signal[:\s]*sell": "SELL",
        r"final\s+signal[:\s]*strong\s+sell": "STRONG_SELL",
    }
    
    for pattern, signal in signal_patterns.items():
        if re.search(pattern, response_lower):
            result["signal"] = signal
            break
    
    # Extract final entry
    entry_match = re.search(r'final\s+entry[:\s]*(\d+\.\d+)', response, re.IGNORECASE)
    if entry_match:
        result["entry"] = float(entry_match.group(1))
    
    # Extract final stop loss
    sl_match = re.search(r'final\s+(?:stop\s+loss|sl)[:\s]*(\d+\.\d+)', response, re.IGNORECASE)
    if sl_match:
        result["stop_loss"] = float(sl_match.group(1))
    
    # Extract position size adjustment
    pos_match = re.search(r'final\s+position\s+size[:\s]*([^.\n]+)', response, re.IGNORECASE)
    if pos_match:
        result["position_size"] = pos_match.group(1).strip()
    
    # Extract adjustment reason (first sentence after adjustment mention)
    reason_match = re.search(r'(because|reason|since)[:\s]*([^.\n]+)', response, re.IGNORECASE)
    if reason_match:
        result["reason"] = reason_match.group(2).strip()
    
    return result

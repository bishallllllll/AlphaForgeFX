from tradingagents.agents.utils.macro_data_tools import build_currency_pair_context

def create_bear_researcher(llm, memory):
    def bear_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")

        current_response = investment_debate_state.get("current_response", "")
        
        # Get Phase 1 analyst reports from state
        market_report = state.get("market_report", "")
        sentiment_report = state.get("sentiment_report", "")
        news_report = state.get("news_report", "")
        macro_report = state.get("macro_report", "")
        
        # Get currency pair and build context
        currency_pair = state.get("instrument", state.get("company_of_interest", "EURUSD"))
        pair_context = build_currency_pair_context(currency_pair)

        curr_situation = f"{market_report}\n\n{sentiment_report}\n\n{news_report}\n\n{macro_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""You are a Bear Analyst analyzing the {currency_pair} currency pair. Your goal is to present a well-reasoned bearish case emphasizing risks, challenges, and negative indicators that could lead to pair weakness or a short bias. Leverage the provided research and data to highlight potential downsides and counter bullish arguments effectively.

{pair_context}

Key points to focus on:

- Interest Rate Risks: Highlight unfavorable interest rate differentials, potential rate cuts, or negative carry trade dynamics.
- Economic Weaknesses: Point out weak economic indicators, low growth, rising inflation, or disappointing data for the base currency.
- Geopolitical/Political Risks: Emphasize instability, trade tensions, or policy uncertainty affecting one or both currencies.
- Technical Weakness: Use support/resistance, trend reversals, or momentum weakness to support the bearish case.
- Bear Counterpoints: Critically analyze the bull argument with specific data and sound reasoning, exposing weaknesses or over-optimistic assumptions about the pair.
- Engagement: Present your argument in a conversational style, directly engaging with the bull analyst's points and debating effectively rather than simply listing facts.

Resources available:

Technical Analysis Report: {market_report}
Trader Sentiment Report: {sentiment_report}
News & Events Report: {news_report}
Macroeconomic Analysis Report: {macro_report}
Conversation history of the debate: {history}
Last bull argument: {current_response}
Reflections from similar trading situations: {past_memory_str}

Deliver a compelling bearish argument for {currency_pair}, refute the bull's claims with specific evidence, and engage in a dynamic debate that demonstrates the risks and weaknesses of the pair. Learn from past reflections and mistakes.
"""

        response = llm.invoke(prompt)

        argument = f"Bear Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node

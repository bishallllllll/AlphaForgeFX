from tradingagents.agents.utils.macro_data_tools import build_currency_pair_context

def create_bull_researcher(llm, memory):
    def bull_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

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

        prompt = f"""You are a Bull Analyst analyzing the {currency_pair} currency pair. Your task is to build a strong, evidence-based bullish case emphasizing opportunities, favorable economic conditions, and positive technical/sentiment indicators. Leverage the provided research and data to address concerns and counter bearish arguments effectively.

{pair_context}

Key points to focus on:

- Interest Rate Opportunities: Highlight favorable interest rate differentials, policy divergence favoring the base currency, or forward rate curve implications.
- Economic Strength: Emphasize strong economic data, GDP growth, low unemployment, or disinflation in the base currency country.
- Positive Technicals: Use support/resistance, trend strength, RSI readings, moving average alignment, or breakout patterns to support the bullish case.
- Sentiment Strength: Leveraging trader positioning and social sentiment as contrarian or confirmatory indicators.
- Bear Counterpoints: Critically analyze the bear argument with specific data and sound reasoning, addressing concerns thoroughly and showing why the bull perspective holds stronger merit.
- Engagement: Present your argument in a conversational style, engaging directly with the bear analyst's points and debating effectively rather than just listing data.

Resources available:

Technical Analysis Report: {market_report}
Trader Sentiment Report: {sentiment_report}
News & Events Report: {news_report}
Macroeconomic Analysis Report: {macro_report}
Conversation history of the debate: {history}
Last bear argument: {current_response}
Reflections from similar trading situations: {past_memory_str}

Deliver a compelling bullish argument for {currency_pair}, refute the bear's concerns with specific evidence, and engage in a dynamic debate that demonstrates the strengths and opportunities of the pair. Learn from past reflections and mistakes.
"""

        response = llm.invoke(prompt)

        argument = f"Bull Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node

"""
Forex Market Analyst

Analyzes technical indicators and price action for currency pairs.
Adapted for forex trading with relevant indicators for currency markets.
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tradingagents.agents.utils.agent_utils import (
    build_instrument_context,
    get_indicators,
    get_language_instruction,
    get_stock_data,
)
from tradingagents.agents.utils.macro_data_tools import build_currency_pair_context


def create_forex_market_analyst(llm):
    """
    Create a Market Analyst node for forex trading.
    
    Analyzes technical indicators and price action for currency pairs.
    
    Args:
        llm: Language model instance to use for analysis
        
    Returns:
        Function that analyzes technical conditions for a currency pair
    """
    
    def forex_market_analyst_node(state):
        # Get currency pair from state
        currency_pair = state.get("instrument", state.get("company_of_interest", "EURUSD"))
        current_date = state["trade_date"]
        
        # Use both regular instrument context and forex-specific pair context
        instrument_context = build_instrument_context(currency_pair)
        pair_context = build_currency_pair_context(currency_pair)

        tools = [
            get_stock_data,
            get_indicators,
        ]

        system_message = (
            """You are a technical analyst for forex markets, specializing in analyzing currency pairs. 
Your role is to select **relevant technical indicators** for analyzing the currency pair's technical structure.
Choose 5-8 indicators that provide complementary insights without redundancy.

**Key Indicator Categories for Forex:**

**Trend Indicators (Choose 1-2):**
- close_50_sma: 50-period SMA - Medium-term trend direction for intraday/swing trading
- close_200_sma: 200-period SMA - Longer-term trend context (daily/weekly timeframe)
- close_10_ema: 10-period EMA - Highly responsive for catching momentum shifts

**Momentum Indicators (Choose 1-2):**
- macd: MACD Main - Identifies momentum and trend changes; watch for crossovers
- rsi: RSI - Detects overbought/oversold levels; excellent for range-bound pairs
- macdh: MACD Histogram - Shows momentum strength and potential reversals

**Volatility Indicators (Choose 1-2):**
- atr: ATR - Critical for forex risk management and stop-loss placement
- boll_ub / boll_lb: Bollinger Bands - Identify breakout zones and volatility compression
- boll: Bollinger Middle - Dynamic support/resistance level

**Volume Analysis:**
- vwma: VWMA - Less relevant for forex spot, but useful if analyzing forex futures/CFDs

**Forex-Specific Analysis Notes:**
1. **Support/Resistance Levels**: Identify key psychological levels (1.2000, 1.1950, 100.00 pips)
2. **Trend Structure**: Recognize higher highs/lows for uptrends, lower highs/lows for downtrends
3. **Volatility Analysis**: Use ATR to understand typical daily ranges and potential breakouts
4. **Divergence Patterns**: Watch for RSI/MACD divergence signaling trend reversals
5. **Timeframe Alignment**: Discuss confluence of signals across multiple timeframes (4H, Daily, Weekly)

**Key Forex Considerations:**
- Forex pairs trend strongly; use moving average crosses for trend confirmation
- Range-bound pairs benefit from RSI and Bollinger Band mean reversion strategies
- High-volatility periods (NFP, ECB, Fed decisions) can break technical patterns
- Carry trade considerations: higher interest rate currency often appreciates in calm markets

Write a comprehensive technical analysis report that:
- Identifies the current trend direction and strength
- Analyzes key support and resistance levels
- Assesses momentum using selected indicators
- Identifies potential entry/exit levels
- Highlights upcoming technical setups
- Provides actionable trading signals with confluences

First call get_stock_data to fetch price data, then call get_indicators with selected indicator names.
Ensure your report includes a summary table of key technical levels and signals."""
            + " Make sure to write in clear, actionable language for traders."
            + get_language_instruction()
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants. "
                    "Use the provided tools to progress towards answering the question. "
                    "If you are unable to fully answer, that's OK; another assistant with different tools "
                    "will help where you left off. Execute what you can to make progress. "
                    "If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**, "
                    "prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop. "
                    "You have access to the following tools: {tool_names}.\n{system_message}\n"
                    "For your reference, the current date is {current_date}.\n{instrument_context}\n{pair_context}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(instrument_context=instrument_context)
        prompt = prompt.partial(pair_context=pair_context)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "market_report": report,
        }

    return forex_market_analyst_node

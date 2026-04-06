"""
Macroeconomic Analyst for Forex Trading

Analyzes macroeconomic fundamentals, central bank policies, 
and economic calendar events to assess forex trading opportunities.

This analyst replaces the Fundamentals Analyst for forex-specific trading.
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tradingagents.agents.utils.agent_utils import get_language_instruction
from tradingagents.agents.utils.macro_data_tools import (
    get_interest_rates,
    get_economic_calendar,
    get_macro_indicators,
    get_central_bank_policy,
    get_geopolitical_risk,
    build_currency_pair_context,
)


def create_macro_analyst(llm):
    """
    Create a Macro Analyst node for forex trading.
    
    Analyzes macroeconomic factors, interest rates, central bank policies,
    and upcoming economic events to inform forex trading decisions.
    
    Args:
        llm: Language model instance to use for analysis
        
    Returns:
        Function that analyzes macro conditions for a given currency pair
    """
    
    def macro_analyst_node(state):
        # Get currency pair from state
        currency_pair = state.get("instrument", state.get("company_of_interest", "EURUSD"))
        current_date = state["trade_date"]
        
        # Build context for the currency pair
        pair_context = build_currency_pair_context(currency_pair)
        
        # Define available tools for macro analysis
        tools = [
            get_interest_rates,
            get_economic_calendar,
            get_macro_indicators,
            get_central_bank_policy,
            get_geopolitical_risk,
        ]
        
        # Detailed system message for macro analysis
        system_message = (
            "You are a forex macroeconomic analyst tasked with analyzing fundamental conditions "
            "for currency trading. Your role is to provide a comprehensive macroeconomic analysis "
            "covering:\n\n"
            
            "1. **Interest Rate Analysis**: Compare policy rates between the two currencies, analyze "
            "central bank stance (hawkish/dovish), and assess rate differential implications.\n\n"
            
            "2. **Economic Indicators**: Analyze inflation, employment, GDP growth, and trade balance "
            "for both countries. Look for diverging trends that would favor one currency.\n\n"
            
            "3. **Central Bank Policy**: Review latest policy statements, forward guidance, and "
            "next meeting schedules. Assess if rates are likely to rise, hold, or fall.\n\n"
            
            "4. **Economic Calendar**: Identify high-impact upcoming data releases. Analyze consensus "
            "expectations and previous readings to anticipate market reactions.\n\n"
            
            "5. **Geopolitical Risk**: Consider political developments, trade tensions, and safe-haven "
            "flows that might affect the currency pair.\n\n"
            
            "Write a comprehensive macroeconomic report that:\n"
            "- Compares macro conditions between the base and quote currencies\n"
            "- Identifies interest rate and inflation differentials\n"
            "- Assesses central bank policy divergence\n"
            "- Highlights upcoming high-impact events and expected market reactions\n"
            "- Provides specific, actionable insights for traders\n"
            "- Includes a summary table organizing key macro factors\n\n"
            
            "Use the available tools strategically:\n"
            "- Use `get_interest_rates` for current rates and policy stances\n"
            "- Use `get_central_bank_policy` for detailed policy statements and guidance\n"
            "- Use `get_macro_indicators` for inflation, GDP, employment, and trade data\n"
            "- Use `get_economic_calendar` to identify upcoming high-impact releases\n"
            "- Use `get_geopolitical_risk` to assess political/geopolitical factors\n\n"
            
            "Focus on factors that drive currency movements: interest rate differentials, "
            "inflation divergence, growth disparities, and policy divergence.\n\n"
            
            + get_language_instruction()
        )
        
        # Create the prompt template
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
                    "For your reference, the current date is {current_date}.\n{pair_context}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        
        # Fill in template variables
        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(pair_context=pair_context)
        
        # Create the chain with tools
        chain = prompt | llm.bind_tools(tools)
        
        # Invoke the chain with current state messages
        result = chain.invoke(state["messages"])
        
        # Extract report if no tool calls were made
        report = ""
        if len(result.tool_calls) == 0:
            report = result.content
        
        # Return updated state
        return {
            "messages": [result],
            "macro_report": report,
        }
    
    return macro_analyst_node

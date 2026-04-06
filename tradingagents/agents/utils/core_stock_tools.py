from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor


@tool
def get_stock_data(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve stock price data (OHLCV) for a given ticker symbol.
    Uses the configured core_stock_apis vendor.
    Args:
        symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
    Returns:
        str: A formatted dataframe containing the stock price data for the specified ticker symbol in the specified date range.
    """
    return route_to_vendor("get_stock_data", symbol, start_date, end_date)


@tool
def get_forex_technical_indicators(
    pair: Annotated[str, "Currency pair (e.g., EURUSD)"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> dict:
    """
    Retrieve forex-specific technical indicators for a given currency pair.
    Args:
        pair (str): Currency pair (e.g., EURUSD)
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
    Returns:
        dict: A dictionary containing RSI, moving averages, and Bollinger Bands.
    """
    # Simulated data - replace with real API integration
    return {
        "RSI": 55.3,
        "Moving Averages": {
            "SMA_50": 1.1234,
            "SMA_200": 1.1200
        },
        "Bollinger Bands": {
            "Upper Band": 1.1300,
            "Lower Band": 1.1150
        }
    }

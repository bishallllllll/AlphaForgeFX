"""
Macroeconomic data tools for forex trading analysis.
Provides tools for accessing interest rates, economic calendar data, 
central bank policies, and macroeconomic indicators.
"""

from langchain_core.tools import tool
from datetime import datetime, timedelta
import json


@tool
def get_interest_rates(
    currencies: list = None,
    look_back_days: int = 30,
) -> dict:
    """
    Get current and historical interest rates for major currencies.
    
    This tool retrieves the latest official rates set by central banks,
    including policy rates and discount rates.
    
    Args:
        currencies: List of currency codes (e.g., ['USD', 'EUR', 'GBP', 'JPY'])
                   If None, returns major currency rates
        look_back_days: Number of days of historical rate data to include
    
    Returns:
        Dictionary with current rates, recent trend, and policy stance
        
    Example:
        {
            'USD': {
                'current_rate': 5.25,
                'last_change': '2024-01-31',
                'central_bank': 'Federal Reserve',
                'policy_stance': 'Hawkish - Pausing rate hikes'
            },
            'EUR': {
                'current_rate': 4.25,
                'last_change': '2024-01-25',
                'central_bank': 'European Central Bank',
                'policy_stance': 'Neutral - Holding steady'
            }
        }
    """
    if currencies is None:
        currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD']
    
    # Simulated/mock data - in production, connect to real APIs like:
    # - FRED (Federal Reserve Economic Data)
    # - ECB Statistical Data Warehouse
    # - Bank of England API
    # - Other central bank APIs
    
    rates_data = {
        'USD': {
            'current_rate': 5.25,
            'last_change': '2024-01-31',
            'central_bank': 'Federal Reserve (Fed)',
            'policy_stance': 'Hawkish - Holding rates steady after hiking cycle',
            'next_meeting': '2024-03-19-20',
            'market_expectation': 'No change expected'
        },
        'EUR': {
            'current_rate': 4.25,
            'last_change': '2024-01-25',
            'central_bank': 'European Central Bank (ECB)',
            'policy_stance': 'Neutral - Data dependent, may pause hikes',
            'next_meeting': '2024-03-07',
            'market_expectation': 'No change, potential future cuts'
        },
        'GBP': {
            'current_rate': 5.25,
            'last_change': '2023-12-14',
            'central_bank': 'Bank of England (BoE)',
            'policy_stance': 'Hawkish - Holding higher for longer',
            'next_meeting': '2024-03-21',
            'market_expectation': 'No change, cuts expected later'
        },
        'JPY': {
            'current_rate': -0.1,
            'last_change': '2024-01-23',
            'central_bank': 'Bank of Japan (BoJ)',
            'policy_stance': 'Dovish - Ultra-loose monetary policy',
            'next_meeting': '2024-03-19-20',
            'market_expectation': 'May begin normalization this year'
        },
        'CHF': {
            'current_rate': 1.75,
            'last_change': '2023-12-14',
            'central_bank': 'Swiss National Bank (SNB)',
            'policy_stance': 'Hawkish - Fighting inflation aggressively',
            'next_meeting': '2024-03-21',
            'market_expectation': 'Will likely hold or continue hiking'
        },
        'CAD': {
            'current_rate': 4.25,
            'last_change': '2023-10-25',
            'central_bank': 'Bank of Canada (BoC)',
            'policy_stance': 'Neutral - On hold after hiking cycle',
            'next_meeting': '2024-03-06',
            'market_expectation': 'May begin cutting rates soon'
        },
        'AUD': {
            'current_rate': 4.35,
            'last_change': '2023-11-07',
            'central_bank': 'Reserve Bank of Australia (RBA)',
            'policy_stance': 'Neutral - Holding rates steady',
            'next_meeting': '2024-02-06',
            'market_expectation': 'Likely to hold, eventual cuts possible'
        },
        'NZD': {
            'current_rate': 5.50,
            'last_change': '2023-11-07',
            'central_bank': 'Reserve Bank of New Zealand (RBNZ)',
            'policy_stance': 'Hawkish - Higher for longer approach',
            'next_meeting': '2024-02-07',
            'market_expectation': 'Will likely hold rates'
        }
    }
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'data': {k: v for k, v in rates_data.items() if k in currencies},
        'note': 'This is demonstration data. Connect to real central bank APIs (FRED, ECB-API, BoE API, etc.) for production.'
    }
    
    return result


@tool
def get_economic_calendar(
    currencies: list = None,
    look_ahead_days: int = 14,
    importance: str = 'high'
) -> dict:
    """
    Get upcoming economic events and data releases for major economies.
    
    Returns the economic calendar with key events like NFP, CPI, GDP, 
    interest rate decisions, etc. that drive currency movements.
    
    Args:
        currencies: List of country codes (e.g., ['US', 'EU', 'UK', 'JP'])
        look_ahead_days: Days ahead to look (default 14 days)
        importance: Filter by importance ('high', 'medium', 'low', 'all')
    
    Returns:
        Sorted list of upcoming economic events with expectations and impact
        
    Example:
        {
            'events': [
                {
                    'date': '2024-02-02',
                    'time': '13:30 UTC',
                    'country': 'US',
                    'event': 'Non-Farm Payroll (NFP)',
                    'forecast': '180K',
                    'previous': '216K',
                    'importance': 'high',
                    'impact_on_pairs': ['EURUSD', 'GBPUSD', 'NZDUSD']
                }
            ]
        }
    """
    if currencies is None:
        currencies = ['US', 'EU', 'UK', 'JP', 'CH', 'CA', 'AU', 'NZ']
    
    # Simulated economic calendar
    # In production, integrate with:
    # - Investing.com Calendar API
    # - Forex Factory API
    # - Economic Indicators APIs from stat agencies
    
    calendar_events = [
        {
            'date': '2024-02-02',
            'time': '13:30 UTC',
            'country': 'US',
            'event': 'Non-Farm Payroll (NFP)',
            'forecast': '180K',
            'previous': '216K',
            'importance': 'high',
            'impact_on_pairs': ['EURUSD', 'GBPUSD', 'NZDUSD', 'AUDUSD'],
            'volatility_expected': 'Very High'
        },
        {
            'date': '2024-02-02',
            'time': '13:30 UTC',
            'country': 'US',
            'event': 'Average Hourly Earnings YoY',
            'forecast': '4.0%',
            'previous': '4.0%',
            'importance': 'high',
            'impact_on_pairs': ['EURUSD', 'GBPUSD'],
            'volatility_expected': 'High'
        },
        {
            'date': '2024-02-05',
            'time': '15:00 UTC',
            'country': 'US',
            'event': 'ISM Non-Manufacturing PMI',
            'forecast': '52.5',
            'previous': '52.0',
            'importance': 'medium',
            'impact_on_pairs': ['EURUSD', 'GBPUSD'],
            'volatility_expected': 'Medium'
        },
        {
            'date': '2024-02-07',
            'time': '10:00 UTC',
            'country': 'EU',
            'event': 'ECB Interest Rate Decision',
            'forecast': 'No change (4.50%)',
            'previous': '4.50%',
            'importance': 'high',
            'impact_on_pairs': ['EURUSD', 'EURGBP', 'EURJPY'],
            'volatility_expected': 'Very High'
        },
        {
            'date': '2024-02-14',
            'time': '18:00 UTC',
            'country': 'US',
            'event': 'CPI (Consumer Price Index) YoY',
            'forecast': '3.1%',
            'previous': '3.4%',
            'importance': 'high',
            'impact_on_pairs': ['EURUSD', 'GBPUSD', 'USDJPY'],
            'volatility_expected': 'Very High'
        }
    ]
    
    # Filter by importance if requested
    if importance != 'all':
        calendar_events = [e for e in calendar_events if e['importance'] == importance or importance == 'all']
    
    # Filter by currencies if specified
    if currencies:
        calendar_events = [e for e in calendar_events if e['country'] in currencies]
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'look_ahead_days': look_ahead_days,
        'events': calendar_events,
        'note': 'Connect to Investing.com API or Forex Factory for real-time calendar updates'
    }
    
    return result


@tool
def get_macro_indicators(
    countries: list = None,
    indicators: list = None,
) -> dict:
    """
    Get key macroeconomic indicators for major economies.
    
    Provides current values and trends for: inflation (CPI/PPI), 
    employment, GDP growth, trade balance, etc.
    
    Args:
        countries: List of country codes (e.g., ['US', 'EU', 'UK'])
        indicators: Specific indicators to fetch
                   (e.g., ['CPI', 'GDP', 'Unemployment', 'Trade_Balance'])
                   If None, returns all major indicators
    
    Returns:
        Dictionary with indicator values, trends, and analysis
        
    Example:
        {
            'US': {
                'CPI_YoY': {'current': 3.1, 'previous': 3.4, 'trend': 'down'},
                'GDP_Annualized': {'current': 2.5, 'previous': 2.8, 'trend': 'down'},
                'Unemployment_Rate': {'current': 3.7, 'previous': 3.8, 'trend': 'down'}
            }
        }
    """
    if countries is None:
        countries = ['US', 'EU', 'UK', 'JP']
    
    if indicators is None:
        indicators = ['CPI_YoY', 'GDP_Annualized', 'Unemployment_Rate', 'Trade_Balance', 'Inflation_Expectation']
    
    # Simulated macro indicators
    # In production, connect to:
    # - FRED (US Federal Reserve Economic Data)
    # - OECD databases
    # - Stat agencies (BLS, Eurostat, etc.)
    
    macro_data = {
        'US': {
            'CPI_YoY': {'current': 3.1, 'previous': 3.4, 'date': '2024-01-15', 'trend': 'down', 'unit': '%'},
            'GDP_Annualized': {'current': 2.5, 'previous': 2.8, 'date': '2023-Q4', 'trend': 'down', 'unit': '%'},
            'Unemployment_Rate': {'current': 3.7, 'previous': 3.8, 'date': '2024-01-15', 'trend': 'stable', 'unit': '%'},
            'Trade_Balance': {'current': -73.1, 'previous': -71.8, 'date': '2023-12', 'trend': 'worse', 'unit': 'Billion USD'},
            'Inflation_Expectation': {'current': 2.4, 'previous': 2.3, 'date': '2024-01', 'trend': 'up', 'unit': '%'}
        },
        'EU': {
            'CPI_YoY': {'current': 2.4, 'previous': 2.8, 'date': '2024-01-15', 'trend': 'down', 'unit': '%'},
            'GDP_Annualized': {'current': 0.5, 'previous': 0.0, 'date': '2023-Q4', 'trend': 'up', 'unit': '%'},
            'Unemployment_Rate': {'current': 6.1, 'previous': 6.2, 'date': '2023-12', 'trend': 'down', 'unit': '%'},
            'Trade_Balance': {'current': 18.7, 'previous': 15.2, 'date': '2023-12', 'trend': 'better', 'unit': 'Billion EUR'},
            'Inflation_Expectation': {'current': 2.1, 'previous': 2.2, 'date': '2024-01', 'trend': 'down', 'unit': '%'}
        },
        'UK': {
            'CPI_YoY': {'current': 4.0, 'previous': 4.4, 'date': '2024-01-15', 'trend': 'down', 'unit': '%'},
            'GDP_Annualized': {'current': 0.3, 'previous': 0.1, 'date': '2023-Q4', 'trend': 'up', 'unit': '%'},
            'Unemployment_Rate': {'current': 3.9, 'previous': 4.0, 'date': '2023-12', 'trend': 'stable', 'unit': '%'},
            'Trade_Balance': {'current': -21.4, 'previous': -19.8, 'date': '2023-12', 'trend': 'worse', 'unit': 'Billion GBP'},
            'Inflation_Expectation': {'current': 2.0, 'previous': 2.1, 'date': '2024-01', 'trend': 'down', 'unit': '%'}
        },
        'JP': {
            'CPI_YoY': {'current': 2.7, 'previous': 2.9, 'date': '2023-12-15', 'trend': 'down', 'unit': '%'},
            'GDP_Annualized': {'current': 1.3, 'previous': 1.9, 'date': '2023-Q3', 'trend': 'down', 'unit': '%'},
            'Unemployment_Rate': {'current': 2.5, 'previous': 2.4, 'date': '2023-12', 'trend': 'up', 'unit': '%'},
            'Trade_Balance': {'current': 11.3, 'previous': 9.8, 'date': '2023-12', 'trend': 'better', 'unit': 'Billion JPY'},
            'Inflation_Expectation': {'current': 1.9, 'previous': 2.0, 'date': '2024-01', 'trend': 'down', 'unit': '%'}
        }
    }
    
    # Filter by requested indicators
    result = {}
    for country in countries:
        if country in macro_data:
            result[country] = {k: v for k, v in macro_data[country].items() if k in indicators}
    
    return {
        'timestamp': datetime.now().isoformat(),
        'data': result,
        'note': 'Connect to FRED, OECD, and national stat agencies for real-time data'
    }


@tool
def get_central_bank_policy(
    central_banks: list = None,
) -> dict:
    """
    Get latest central bank policy statements, minutes, and guidance.
    
    Provides recent policy announcements, forward guidance, and 
    analysis of central bank stances on inflation, growth, and rate path.
    
    Args:
        central_banks: List of central banks (e.g., ['Fed', 'ECB', 'BoE', 'BoJ'])
                      If None, returns all major central banks
    
    Returns:
        Dictionary with policy statements, next meeting dates, and forward guidance
        
    Example:
        {
            'Fed': {
                'last_decision_date': '2024-01-31',
                'next_decision_date': '2024-03-19',
                'current_policy_rate': 5.25,
                'recent_statement': 'Holding steady...',
                'forward_guidance': 'Pausing rate hikes, data dependent'
            }
        }
    """
    if central_banks is None:
        central_banks = ['Fed', 'ECB', 'BoE', 'BoJ', 'SNB', 'BoC']
    
    policy_data = {
        'Fed': {
            'full_name': 'Federal Reserve',
            'last_decision_date': '2024-01-31',
            'next_decision_date': '2024-03-19',
            'current_policy_rate': 5.25,
            'rate_change': 'No change (hold steady)',
            'policy_stance': 'Hawkish - Higher for longer',
            'key_points': [
                'Inflation has made progress but remains above 2% target',
                'Labor market remains solid with strong job creation',
                'Will likely hold rates for extended period',
                'Future cuts dependent on inflation data'
            ],
            'forward_guidance': 'Cooling inflation, but holding rates to ensure progress continues',
            'source': 'FOMC Statement and Dot Plot'
        },
        'ECB': {
            'full_name': 'European Central Bank',
            'last_decision_date': '2024-01-25',
            'next_decision_date': '2024-03-07',
            'current_policy_rate': 4.25,
            'rate_change': 'No change (hold steady)',
            'policy_stance': 'Neutral - Data dependent',
            'key_points': [
                'Inflation declining toward 2% target',
                'Economic growth weak but stabilizing',
                'Will maintain data-dependent approach',
                'Rate cuts possible if inflation continues slowing'
            ],
            'forward_guidance': 'A patient, data-dependent approach, with possible future cuts',
            'source': 'ECB Press Release and Monetary Policy Statement'
        },
        'BoE': {
            'full_name': 'Bank of England',
            'last_decision_date': '2023-12-14',
            'next_decision_date': '2024-02-08',
            'current_policy_rate': 5.25,
            'rate_change': 'No change (hold steady)',
            'policy_stance': 'Hawkish - Higher for longer',
            'key_points': [
                'Inflation persistent and above target',
                'Services inflation particularly sticky',
                'Holding rates to anchor expectations',
                'First cuts likely to come later than markets expect'
            ],
            'forward_guidance': 'Holding rates high for longer to combat sticky inflation',
            'source': 'MPC Statement'
        },
        'BoJ': {
            'full_name': 'Bank of Japan',
            'last_decision_date': '2024-01-23',
            'next_decision_date': '2024-03-19',
            'current_policy_rate': -0.1,
            'rate_change': 'No change (hold steady)',
            'policy_stance': 'Dovish - Ultra-loose policy',
            'key_points': [
                'Maintaining negative interest rates',
                'Yield curve control in place (10Y JGB at 1%)',
                'Gradually normalizing monetary policy',
                'May exit negative rates later in 2024'
            ],
            'forward_guidance': 'Gradual normalization of monetary policy, potential first rate hike this year',
            'source': 'BoJ Press Release'
        },
        'SNB': {
            'full_name': 'Swiss National Bank',
            'last_decision_date': '2023-12-14',
            'next_decision_date': '2024-03-21',
            'current_policy_rate': 1.75,
            'rate_change': 'No change (on hold)',
            'policy_stance': 'Hawkish - Fighting inflation',
            'key_points': [
                'Keeping rates elevated to fight inflation',
                'May continue hiking if inflation persists',
                'Strong CHF helps anchor inflation expectations',
                'Limited room for further hikes'
            ],
            'forward_guidance': 'Will continue to keep rates restrictive, ready to hike further if needed',
            'source': 'SNB Monetary Policy Statement'
        },
        'BoC': {
            'full_name': 'Bank of Canada',
            'last_decision_date': '2023-10-25',
            'next_decision_date': '2024-03-06',
            'current_policy_rate': 4.25,
            'rate_change': 'No change (on hold)',
            'policy_stance': 'Neutral - On hold',
            'key_points': [
                'Held rates after hiking cycle ended',
                'Inflation moderating toward 2% target',
                'Weak economic growth supports potential cuts',
                'Rate cuts may begin in spring 2024'
            ],
            'forward_guidance': 'Likely to begin rate cuts in coming months if inflation continues moderating',
            'source': 'BoC Press Release'
        }
    }
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'data': {k: v for k, v in policy_data.items() if k in central_banks},
        'note': 'Subscribe to central bank press releases and calendars for real-time updates'
    }
    
    return result


@tool
def get_geopolitical_risk(
    region: str = 'global',
    look_back_days: int = 7
) -> dict:
    """
    Get current geopolitical risk events impacting currency markets.
    
    Tracks geopolitical developments, trade tensions, political risks,
    and other events that affect currency valuations and volatility.
    
    Args:
        region: Region to analyze ('global', 'Europe', 'Asia', 'Americas')
        look_back_days: Days of historical events to include
    
    Returns:
        Dictionary with geopolitical events and their market impact
        
    Example:
        {
            'events': [
                {
                    'date': '2024-02-01',
                    'region': 'Europe',
                    'event': 'NATO discusses Ukraine military aid',
                    'risk_level': 'medium',
                    'affected_currencies': ['EUR', 'GBP'],
                    'market_reaction': 'EUR weakness expected'
                }
            ]
        }
    """
    
    geopolitical_events = [
        {
            'date': '2024-02-01',
            'region': 'Europe',
            'event': 'NATO increases military exercises near Ukraine',
            'risk_level': 'medium',
            'affected_currencies': ['EUR', 'GBP', 'PLN'],
            'impact_description': 'May strengthen safe-haven USD/CHF, weaken EUR',
            'market_implication': 'Expect EUR weakness if tensions escalate'
        },
        {
            'date': '2024-01-30',
            'region': 'Global',
            'event': 'US-China trade negotiations begin',
            'risk_level': 'medium',
            'affected_currencies': ['USD', 'CNY', 'AUD'],
            'impact_description': 'Risk-on/risk-off sentiment swings',
            'market_implication': 'Positive for commodity currencies (AUD, CAD) if deal progresses'
        },
        {
            'date': '2024-01-28',
            'region': 'Middle East',
            'event': 'Houthi attacks on shipping in Red Sea continue',
            'risk_level': 'low-medium',
            'affected_currencies': ['USD', 'CHF', 'JPY'],
            'impact_description': 'Supports safe-haven demand, increases oil risk premium',
            'market_implication': 'Supports CHF and JPY as safe haven, USD mixed'
        },
        {
            'date': '2024-01-25',
            'region': 'UK/Europe',
            'event': 'UK Parliament debates Brexit-related fiscal rules',
            'risk_level': 'low',
            'affected_currencies': ['GBP', 'EUR'],
            'impact_description': 'Limited near-term currency impact',
            'market_implication': 'GBP could weaken if political uncertainty rises'
        }
    ]
    
    # Filter by region if specified
    if region != 'global':
        geopolitical_events = [e for e in geopolitical_events 
                              if e['region'] == region or e['region'] == 'Global']
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'region': region,
        'look_back_days': look_back_days,
        'events': geopolitical_events,
        'risk_assessment': 'Monitor developments closely; geopolitical events can drive sharp currency moves',
        'note': 'Monitor news sources (Reuters, Bloomberg, FT) and geopolitical risk indices'
    }
    
    return result


def build_currency_pair_context(pair: str) -> str:
    """
    Build context string for a currency pair, identifying base and quote.
    
    Args:
        pair: Currency pair code (e.g., 'EURUSD', 'GBPJPY')
    
    Returns:
        Formatted context string explaining both currencies in the pair
    """
    # Extract base and quote currencies
    if len(pair) >= 6:
        base = pair[:3]
        quote = pair[3:6]
    else:
        return f"Currency pair: {pair}"
    
    context = (
        f"You are analyzing the currency pair {pair}, where:\n"
        f"- Base Currency: {base} (the currency being bought/sold)\n"
        f"- Quote Currency: {quote} (the pricing currency)\n"
        f"- A rise in {pair} means {base} is strengthening relative to {quote}\n"
        f"- Analyze both {base} and {quote} macro conditions, interest rates, and economic outlooks\n"
        f"- Compare interest rate differentials: ({base} rates - {quote} rates)\n"
        f"- Higher interest rate differential favors buying {pair}"
    )
    
    return context

"""
Macroeconomic data tools for forex trading analysis.
Provides tools for accessing interest rates, economic calendar data, 
central bank policies, and macroeconomic indicators.
"""

from langchain_core.tools import tool
from datetime import datetime, timedelta
import json
import logging
import os

# Import the Forex Factory scraper
try:
    from tradingagents.dataflows.forex_factory_scraper import (
        ForexFactoryScraper,
        get_economic_calendar as get_ff_calendar,
        get_high_impact_events
    )
    FOREX_FACTORY_AVAILABLE = True
except ImportError:
    FOREX_FACTORY_AVAILABLE = False
    logging.warning("Forex Factory scraper not available, will use demo data")

# Import new Tier 1 data sources
try:
    from tradingagents.dataflows.twelve_data_forex import (
        get_realtime_forex_price,
        get_forex_intraday
    )
    TWELVE_DATA_AVAILABLE = True
except ImportError:
    TWELVE_DATA_AVAILABLE = False
    logging.warning("Twelve Data forex not available")

try:
    from tradingagents.dataflows.central_bank_communications import (
        get_all_cb_sentiment,
        get_rate_differential,
        analyze_pair_policy
    )
    CB_COMMS_AVAILABLE = True
except ImportError:
    CB_COMMS_AVAILABLE = False
    logging.warning("Central Bank Communications not available")

try:
    from tradingagents.dataflows.cftc_cot import (
        get_cot_positioning,
        compare_cot_positioning,
        get_cot_extremes
    )
    CFTC_COT_AVAILABLE = True
except ImportError:
    CFTC_COT_AVAILABLE = False
    logging.warning("CFTC CoT data not available")

try:
    from tradingagents.dataflows.volatility_indices import (
        get_vix,
        get_move,
        get_all_volatility
    )
    VOLATILITY_AVAILABLE = True
except ImportError:
    VOLATILITY_AVAILABLE = False
    logging.warning("Volatility Indices not available")

logger = logging.getLogger(__name__)


@tool
def get_interest_rates(
    currencies: list = None,
    look_back_days: int = 30,
) -> dict:
    """
    Get current and historical interest rates for major currencies.
    
    This tool retrieves the latest official rates set by central banks,
    including policy rates and discount rates.
    
    Uses FRED API for US rates and historical data where available,
    falls back to demo data for international rates.

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
    
    rates_data = {}
    
    # Try to fetch US Fed Funds Rate from FRED API
    fred_api_key = os.getenv('FRED_API_KEY')
    if fred_api_key and 'USD' in currencies:
        try:
            import requests
            logger.info("[Interest Rates] Using FRED API for US Federal Funds Rate")
            
            fred_url = 'https://api.stlouisfed.org/fred/series/observations'
            params = {
                'series_id': 'FEDFUNDS',
                'api_key': fred_api_key,
                'limit': 1,
                'sort_order': 'desc'
            }
            response = requests.get(fred_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'observations' and len(data['observations']) > 0:
                obs = data['observations'][0]
                rates_data['USD'] = {
                    'current_rate': float(obs['value']),
                    'last_change': obs['date'],
                    'central_bank': 'Federal Reserve (Fed)',
                    'policy_stance': 'Data-dependent, market pricing in holds',
                    'next_meeting': '2024-03-19-20',
                    'market_expectation': 'Hold expected',
                    'source': 'FRED API (Real-time)'
                }
                logger.info(f"[Interest Rates] USD Fed Funds Rate: {obs['value']}%")
        except Exception as e:
            logger.warning(f"[Interest Rates] FRED API failed: {e}, using demo data for USD")
    
    # Add USD to rates_data if still missing (fallback)
    if 'USD' in currencies and 'USD' not in rates_data:
        rates_data['USD'] = {
            'current_rate': 5.25,
            'last_change': '2024-01-31',
            'central_bank': 'Federal Reserve (Fed)',
            'policy_stance': 'Hawkish - Holding rates steady after hiking cycle',
            'next_meeting': '2024-03-19-20',
            'market_expectation': 'No change expected'
        }
    
    # Demo data for other central banks (keep existing demo)
    other_rates = {
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
    
    # Add other currencies from demo data
    for curr in currencies:
        if curr not in rates_data and curr in other_rates:
            rates_data[curr] = other_rates[curr]
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'data': rates_data,
        'note': 'USD rates from FRED API where available, other rates are demo data. Set FRED_API_KEY for real-time US rate data.'
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
    
    Uses the Forex Factory scraper for real data when available,
    falls back to demo data if scraping is blocked.
    
    Args:
        currencies: List of country codes (e.g., ['US', 'EU', 'UK', 'JP'])
        look_ahead_days: Days ahead to look (default 14 days)
        importance: Filter by importance ('high', 'medium', 'low', 'all')
    
    Returns:
        Sorted list of upcoming economic events with expectations and impact
    """
    
    # Try to use Forex Factory scraper for real data
    if FOREX_FACTORY_AVAILABLE:
        try:
            logger.info("[Economic Calendar] Using Forex Factory scraper for real-time data")
            scraper = ForexFactoryScraper()
            
            if importance == 'high':
                ff_events = scraper.get_high_impact_events(days_ahead=look_ahead_days)
            else:
                ff_events = scraper.get_calendar(days_ahead=look_ahead_days)
            
            # Transform Forex Factory events to our format
            result = {
                'timestamp': datetime.now().isoformat(),
                'look_ahead_days': look_ahead_days,
                'events': ff_events,
                'source': 'Forex Factory (Real-time scraper)',
                'importance_filter': importance,
                'total_events': len(ff_events)
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"[Economic Calendar] Forex Factory scraper failed: {e}, using demo data")
    
    # Fallback to demo data
    logger.info("[Economic Calendar] Using demo calendar data")
    
    if currencies is None:
        currencies = ['US', 'EU', 'UK', 'JP', 'CH', 'CA', 'AU', 'NZ']
    
    # Demo economic calendar
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
        'source': 'Demo data (Forex Factory scraper available)',
        'importance_filter': importance,
        'total_events': len(calendar_events)
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
    
    Uses API Ninjas for economic data where available,
    falls back to demo data if API unavailable.
    
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
    
    # Try API Ninjas for real economic data
    api_ninjas_key = os.getenv('API_NINJAS_KEY')
    macro_data = {}
    
    if api_ninjas_key:
        try:
            import requests
            logger.info("[Macro Indicators] Using API Ninjas for economic data")
            
            # API Ninjas endpoint for economic indicators
            api_ninjas_url = 'https://api.api-ninjas.com/v1/markets/economicdata'
            
            for country in countries:
                try:
                    # Map country codes to API Ninjas country parameter
                    country_map = {
                        'US': 'United States',
                        'EU': 'European Union',
                        'UK': 'United Kingdom',
                        'JP': 'Japan',
                        'CA': 'Canada',
                        'CH': 'Switzerland',
                        'AU': 'Australia'
                    }
                    
                    country_name = country_map.get(country, country)
                    headers = {'X-Api-Key': api_ninjas_key}
                    
                    params = {'country': country_name}
                    response = requests.get(api_ninjas_url, headers=headers, params=params, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data:
                        # Transform API Ninjas response to our format
                        macro_data[country] = {
                            'CPI_YoY': {
                                'current': data.get('inflation_rate', 'N/A'),
                                'previous': data.get('inflation_rate_previous', 'N/A'),
                                'date': data.get('date', 'latest'),
                                'trend': 'stable',
                                'unit': '%',
                                'source': 'API Ninjas'
                            },
                            'GDP_Annualized': {
                                'current': data.get('gdp_growth_rate', 'N/A'),
                                'previous': 'N/A',
                                'date': data.get('date', 'latest'),
                                'trend': 'stable',
                                'unit': '%',
                                'source': 'API Ninjas'
                            }
                        }
                        logger.info(f"[Macro Indicators] Retrieved data for {country} from API Ninjas")
                        
                except Exception as e:
                    logger.debug(f"[Macro Indicators] API Ninjas failed for {country}: {e}")
        
        except Exception as e:
            logger.warning(f"[Macro Indicators] API Ninjas connection failed: {e}, using demo data")
    
    # Fallback: Demo macro indicators for any missing countries
    demo_data = {
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
    
    # Fill in any missing countries with demo data
    for country in countries:
        if country not in macro_data and country in demo_data:
            macro_data[country] = demo_data[country]
        elif country not in macro_data:
            # Add default demo for unknown countries
            macro_data[country] = demo_data.get('US', {})
    
    # Filter by requested indicators
    result = {}
    for country in countries:
        if country in macro_data:
            result[country] = {k: v for k, v in macro_data[country].items() if k in indicators}
    
    return {
        'timestamp': datetime.now().isoformat(),
        'data': result,
        'source': 'API Ninjas + Demo fallback',
        'note': 'Real-time data from API Ninjas where available, demo data otherwise. Set API_NINJAS_KEY for live economic data.'
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


# ==================== TIER 1 REAL-TIME DATA SOURCES ====================
# New additions for enhanced accuracy: Real-time forex prices, CB sentiment, CoT positioning, Volatility


@tool
def get_realtime_forex_price(
    currency_pairs: list = None,
    include_bid_ask_history: bool = False
) -> dict:
    """
    Get real-time forex prices with bid/ask spreads from Twelve Data API.
    
    Provides live currency pair quotes with spread analysis for liquidity
    assessment and execution considerations.
    
    Args:
        currency_pairs: List of pairs (e.g., ['EURUSD', 'GBPUSD', 'USDJPY'])
                       If None, returns major pairs
        include_bid_ask_history: If True, includes recent bid/ask history for spread volatility
    
    Returns:
        Dictionary with current prices, spreads, and liquidity metrics
        
    Example:
        {
            'EURUSD': {
                'bid': 1.0850,
                'ask': 1.0851,
                'spread_pips': 0.1,
                'timestamp': '2024-02-01T14:30:45Z',
                'liquidity': 'Very High'
            }
        }
    """
    if currency_pairs is None:
        currency_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'EURGBP']
    
    try:
        if TWELVE_DATA_AVAILABLE:
            logger.info(f"[Realtime Forex] Fetching prices for {currency_pairs} from Twelve Data")
            from tradingagents.dataflows.twelve_data_forex import TwelveDataForex
            
            client = TwelveDataForex()
            prices = {}
            
            for pair in currency_pairs:
                try:
                    price_data = client.get_price(pair)
                    prices[pair] = price_data
                    logger.debug(f"[Realtime Forex] {pair}: {price_data['bid']}/{price_data['ask']}")
                except Exception as e:
                    logger.warning(f"[Realtime Forex] Failed to fetch {pair}: {e}")
                    prices[pair] = {
                        'error': str(e),
                        'note': 'Using fallback demo data',
                        'bid': 1.0850,  # Placeholder
                        'ask': 1.0851
                    }
            
            return {
                'timestamp': datetime.now().isoformat(),
                'data': prices,
                'source': 'Twelve Data API (Real-time)',
                'note': 'Set TWELVE_DATA_API_KEY environment variable for live data'
            }
        else:
            logger.info("[Realtime Forex] Twelve Data not available, using demo data")
            raise ImportError("Twelve Data module not available")
    
    except Exception as e:
        logger.warning(f"[Realtime Forex] Could not fetch live prices: {e}, using demo data")
        
        # Demo data fallback
        demo_prices = {
            'EURUSD': {'bid': 1.0850, 'ask': 1.0851, 'spread_pips': 0.1, 'liquidity': 'Very High'},
            'GBPUSD': {'bid': 1.2680, 'ask': 1.2681, 'spread_pips': 0.1, 'liquidity': 'Very High'},
            'USDJPY': {'bid': 149.85, 'ask': 149.87, 'spread_pips': 2.0, 'liquidity': 'Very High'},
            'AUDUSD': {'bid': 0.6580, 'ask': 0.6581, 'spread_pips': 0.1, 'liquidity': 'High'},
            'USDCAD': {'bid': 1.3485, 'ask': 1.3487, 'spread_pips': 0.2, 'liquidity': 'High'},
            'EURGBP': {'bid': 0.8565, 'ask': 0.8566, 'spread_pips': 0.1, 'liquidity': 'Very High'}
        }
        
        result_prices = {p: demo_prices.get(p, {'bid': 1.0, 'ask': 1.001, 'spread_pips': 0.1}) 
                        for p in currency_pairs}
        
        return {
            'timestamp': datetime.now().isoformat(),
            'data': result_prices,
            'source': 'Demo data (Twelve Data API available)',
            'note': 'Set TWELVE_DATA_API_KEY for live forex prices'
        }


@tool
def get_central_bank_sentiment(
    include_rate_differential: bool = True,
    pair_analysis: str = None
) -> dict:
    """
    Get central bank sentiment analysis and policy guidance for major economies.
    
    Analyzes Fed, ECB, BoJ, and BoE sentiment scores (dovish to hawkish),
    along with rate differentials for carry trade assessment.
    
    Args:
        include_rate_differential: If True, includes carry trade attractiveness
        pair_analysis: Specific pair to analyze (e.g., 'EURUSD' for EUR policy vs USD policy)
    
    Returns:
        Dictionary with CB sentiment scores and policy analysis
        
    Example:
        {
            'Fed': {'sentiment_score': 0.65, 'stance': 'Hawkish', 'rate': 5.25},
            'ECB': {'sentiment_score': 0.35, 'stance': 'Neutral', 'rate': 4.25},
            'carry_trade_analysis': 'EURUSD: High attractiveness (USD 100bps higher)'
        }
    """
    try:
        if CB_COMMS_AVAILABLE:
            logger.info("[CB Sentiment] Fetching from Central Bank Communications module")
            from tradingagents.dataflows.central_bank_communications import (
                CentralBankCommunications,
                get_all_cb_sentiment,
                get_rate_differential,
                analyze_pair_policy
            )
            
            cb_client = CentralBankCommunications()
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'all_banks': cb_client.get_all_central_banks(),
                'source': 'Central Bank Communications Module'
            }
            
            if include_rate_differential:
                result['rate_differentials'] = cb_client.calculate_rate_differential()
                logger.info("[CB Sentiment] Added rate differential analysis")
            
            if pair_analysis:
                result['pair_analysis'] = cb_client.analyze_policy_guidance(pair_analysis)
                logger.info(f"[CB Sentiment] Added policy analysis for {pair_analysis}")
            
            return result
        else:
            raise ImportError("CB Communications module not available")
    
    except Exception as e:
        logger.warning(f"[CB Sentiment] Could not fetch CB data: {e}, using demo data")
        
        # Demo sentiment data
        demo_sentiment = {
            'timestamp': datetime.now().isoformat(),
            'all_banks': {
                'Fed': {
                    'sentiment_score': 0.65,
                    'stance': 'Hawkish',
                    'current_rate': 5.25,
                    'rate_path': 'On Hold',
                    'next_meeting': '2024-03-19',
                    'inflation_view': 'Elevated, making progress',
                    'growth_view': 'Resilient'
                },
                'ECB': {
                    'sentiment_score': 0.35,
                    'stance': 'Neutral to Hawkish',
                    'current_rate': 4.25,
                    'rate_path': 'Data Dependent',
                    'next_meeting': '2024-03-07',
                    'inflation_view': 'Moderating toward target',
                    'growth_view': 'Weak but stabilizing'
                },
                'BoJ': {
                    'sentiment_score': -0.75,
                    'stance': 'Dovish',
                    'current_rate': -0.10,
                    'rate_path': 'Gradual Normalization',
                    'next_meeting': '2024-03-19',
                    'inflation_view': 'Persistent but manageable',
                    'growth_view': 'Moderate'
                },
                'BoE': {
                    'sentiment_score': 0.55,
                    'stance': 'Hawkish',
                    'current_rate': 5.25,
                    'rate_path': 'Higher for Longer',
                    'next_meeting': '2024-02-08',
                    'inflation_view': 'Sticky, especially services',
                    'growth_view': 'Slow'
                }
            },
            'source': 'Demo data',
            'note': 'For real CB sentiment, ensure tradingagents.dataflows.central_bank_communications is available'
        }
        
        if include_rate_differential:
            demo_sentiment['rate_differentials'] = {
                'EURUSD': {'differential': 1.0, 'attractiveness': 'Moderate', 'bias': 'USD favored'},
                'GBPUSD': {'differential': 0.0, 'attractiveness': 'Neutral', 'bias': 'Balanced'},
                'USDJPY': {'differential': 5.35, 'attractiveness': 'Very High', 'bias': 'USD favored'}
            }
        
        return demo_sentiment


@tool
def get_cot_positioning_analysis(
    currencies: list = None,
    detect_extremes: bool = True
) -> dict:
    """
    Get CFTC Commitment of Traders (CoT) positioning data.
    
    Analyzes large-trader vs small-trader (speculator) positioning
    for major currency futures, identifies crowded trades and extremes.
    
    Args:
        currencies: List of currencies to analyze (e.g., ['EUR', 'GBP', 'JPY'])
                   If None, returns all major currencies
        detect_extremes: If True, highlights extreme positioning levels
    
    Returns:
        Dictionary with CoT data and positioning signals
        
    Example:
        {
            'EUR': {
                'large_traders_net_long': 45000,
                'positioning_signal': 0.65,  # -1.0 (bearish) to +1.0 (bullish)
                'extreme': 'Moderately Bullish'
            }
        }
    """
    try:
        if CFTC_COT_AVAILABLE:
            logger.info(f"[CoT Analysis] Fetching positioning for {currencies}")
            from tradingagents.dataflows.cftc_cot import CFTCCommitmentOfTraders
            
            cot_client = CFTCCommitmentOfTraders()
            
            if not currencies:
                currencies = ['EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD']
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'positioning': {},
                'source': 'CFTC Commitment of Traders (Free Public Data)'
            }
            
            for currency in currencies:
                try:
                    pos_data = cot_client.get_cot_positioning(currency)
                    result['positioning'][currency] = pos_data
                    logger.debug(f"[CoT Analysis] {currency}: Signal {pos_data.get('positioning_signal', 'N/A')}")
                except Exception as e:
                    logger.warning(f"[CoT Analysis] Failed for {currency}: {e}")
                    result['positioning'][currency] = {'error': str(e)}
            
            if detect_extremes:
                try:
                    extremes = cot_client.get_positioning_extremes()
                    result['extremes'] = extremes
                    logger.info("[CoT Analysis] Added extreme positioning detection")
                except Exception as e:
                    logger.warning(f"[CoT Analysis] Could not detect extremes: {e}")
            
            return result
        else:
            raise ImportError("CFTC CoT module not available")
    
    except Exception as e:
        logger.warning(f"[CoT Analysis] Could not fetch CoT data: {e}, using demo data")
        
        # Demo CoT data
        demo_cot = {
            'timestamp': datetime.now().isoformat(),
            'positioning': {
                'EUR': {
                    'large_traders_net_long': 45000,
                    'small_traders_net_long': 12000,
                    'open_interest': 500000,
                    'positioning_signal': 0.65,
                    'signal_interpretation': 'Moderately Bullish',
                    'commercial_bias': 'Long Bias'
                },
                'GBP': {
                    'large_traders_net_long': 35000,
                    'small_traders_net_long': 8000,
                    'open_interest': 350000,
                    'positioning_signal': 0.25,
                    'signal_interpretation': 'Slightly Bullish',
                    'commercial_bias': 'Balanced'
                },
                'JPY': {
                    'large_traders_net_long': -55000,
                    'small_traders_net_long': 5000,
                    'open_interest': 600000,
                    'positioning_signal': -0.75,
                    'signal_interpretation': 'Very Bearish',
                    'commercial_bias': 'Short Bias'
                }
            },
            'extremes': {
                'most_bullish': 'EUR',
                'most_bearish': 'JPY',
                'crowded_trades': ['JPY short bias']
            },
            'source': 'Demo data',
            'note': 'For real CFTC data, ensure tradingagents.dataflows.cftc_cot is available'
        }
        
        return demo_cot


@tool
def get_volatility_analysis(
    include_risk_sentiment: bool = True,
    regime_classification: bool = True
) -> dict:
    """
    Get volatility indices (VIX, MOVE, TYVIX) and risk sentiment assessment.
    
    Analyzes equity, bond, and commodity volatility to determine risk regime
    (Risk-On vs Risk-Off) and position sizing recommendations.
    
    Args:
        include_risk_sentiment: If True, includes overall risk sentiment classification
        regime_classification: If True, includes volatility regime (Low/Normal/Elevated/High)
    
    Returns:
        Dictionary with volatility indices and risk assessment
        
    Example:
        {
            'VIX': {'value': 18.5, 'level': 'Normal', 'interpretation': 'Calm equity market'},
            'MOVE': {'value': 121.3, 'level': 'Elevated', 'interpretation': 'Bond uncertainty'},
            'risk_sentiment': 'Balanced',
            'regime': 'Normal Volatility'
        }
    """
    try:
        if VOLATILITY_AVAILABLE:
            logger.info("[Volatility] Fetching indices from Volatility Module")
            from tradingagents.dataflows.volatility_indices import VolatilityIndices
            
            vol_client = VolatilityIndices()
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'indices': {},
                'source': 'Yahoo Finance + Volatility Module'
            }
            
            # Fetch each volatility index
            try:
                vix = vol_client.get_vix()
                result['indices']['VIX'] = vix
                logger.debug(f"[Volatility] VIX: {vix.get('value', 'N/A')}")
            except Exception as e:
                logger.warning(f"[Volatility] Failed to fetch VIX: {e}")
            
            try:
                move = vol_client.get_move_index()
                result['indices']['MOVE'] = move
                logger.debug(f"[Volatility] MOVE: {move.get('value', 'N/A')}")
            except Exception as e:
                logger.warning(f"[Volatility] Failed to fetch MOVE: {e}")
            
            try:
                tyvix = vol_client.get_tyvix()
                result['indices']['TYVIX'] = tyvix
                logger.debug(f"[Volatility] TYVIX: {tyvix.get('value', 'N/A')}")
            except Exception as e:
                logger.warning(f"[Volatility] Failed to fetch TYVIX: {e}")
            
            # Get all indices for comprehensive analysis
            try:
                all_vol = vol_client.get_all_volatility_indices()
                result['all_indices'] = all_vol.get('indicators', {})
                
                if include_risk_sentiment:
                    result['risk_sentiment'] = all_vol.get('risk_sentiment', 'Unknown')
                
                if regime_classification:
                    result['volatility_regime'] = all_vol.get('volatility_regime', 'Unknown')
                
                logger.info("[Volatility] Added comprehensive volatility analysis")
            except Exception as e:
                logger.warning(f"[Volatility] Could not get all indices: {e}")
            
            return result
        else:
            raise ImportError("Volatility module not available")
    
    except Exception as e:
        logger.warning(f"[Volatility] Could not fetch volatility data: {e}, using demo data")
        
        # Demo volatility data
        demo_volatility = {
            'timestamp': datetime.now().isoformat(),
            'indices': {
                'VIX': {
                    'value': 18.5,
                    'level': 'Normal',
                    'interpretation': 'Calm equity market, S&P 500 trading quietly',
                    'range': '10-20 is normal, below 10 is very low, above 30 is elevated'
                },
                'MOVE': {
                    'value': 121.3,
                    'level': 'Elevated',
                    'interpretation': 'Bond market showing elevated volatility',
                    'range': '100-150 is elevated, above 150 is high'
                },
                'TYVIX': {
                    'value': 95.0,
                    'level': 'Normal',
                    'interpretation': '10-Year Treasury volatility is normal',
                    'range': 'Normal is 80-110'
                },
                'OVX': {
                    'value': 28.5,
                    'level': 'Low',
                    'interpretation': 'Oil market is calm'
                },
                'GVZ': {
                    'value': 15.2,
                    'level': 'Very Low',
                    'interpretation': 'Gold volatility is very low, indicating low safe-haven demand'
                }
            },
            'source': 'Demo data',
            'note': 'For real volatility indices, ensure tradingagents.dataflows.volatility_indices is available'
        }
        
        if include_risk_sentiment:
            demo_volatility['risk_sentiment'] = 'Balanced (RISK_ON bias with elevated bond volatility)'
        
        if regime_classification:
            demo_volatility['volatility_regime'] = 'Normal (Mixed signals: Low equity vol, elevated bond vol)'
        
        return demo_volatility

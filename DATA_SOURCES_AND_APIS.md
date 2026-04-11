# AlphaForgeFX: Data Sources & APIs Configuration Guide

This document maps all data requirements for each trading agent and provides instructions on where to obtain them.

---

## 📊 Data Requirements by Agent

### 1. **Market Analyst** 
**Purpose**: Technical analysis for price trends and momentum

#### Data Required:
| Data Type | Details | Current Source | Format |
|-----------|---------|-----------------|--------|
| **OHLCV Data** | Open, High, Low, Close, Volume | YFinance / Alpha Vantage | CSV/JSON |
| **Technical Indicators** | RSI, MACD, Bollinger Bands, ATR, EMA, SMA, VWMA | YFinance / Alpha Vantage | Calculated values |

#### APIs Available:
- **YFinance (FREE)** ✅
  - Status: Active
  - Endpoint: `yfinance` Python library
  - Data: Real-time OHLCV, fundamental data, news
  - Limit: Rate limited (~10 requests/sec)
  
- **Alpha Vantage (FREE tier available)**
  - Status: Active
  - Endpoint: `https://www.alphavantage.co/query`
  - Data: OHLCV, technical indicators
  - API Key: Required
  - Limit: 5 requests/min (free), 500 req/day

#### Setup for Stocks:
```python
# Already configured in default_config.py
"data_vendors": {
    "core_stock_apis": "yfinance",  # or "alpha_vantage"
    "technical_indicators": "yfinance",
}
```

---

### 2. **News Analyst**
**Purpose**: Sentiment and event-driven analysis

#### Data Required:
| Data Type | Details | Current Source | Status |
|-----------|---------|-----------------|--------|
| **News Articles** | Company-specific news, press releases | YFinance / Alpha Vantage | Working |
| **Global News** | Macroeconomic news, market updates | YFinance | Working |
| **News Sentiment** | Positive/negative/neutral sentiment | Optional enhancement | Not implemented |

#### APIs Available:
- **YFinance (Built-in)** ✅
  - News endpoint included
  - No API key required
  
- **NewsAPI** (Optional enhancement)
  - Endpoint: `https://newsapi.org/v2`
  - API Key: Required (free tier available)
  - Coverage: 50+ sources
  - Rate Limit: 100 requests/day (free)
  - Website: https://newsapi.org

- **Finnhub** (Alternative)
  - Endpoint: `https://finnhub.io`
  - API Key: Required (free: $0, but limited)
  - Coverage: Financial news from 20+ sources
  - Website: https://finnhub.io

---

### 3. **Social Media Analyst**
**Purpose**: Public sentiment and social discussion analysis

#### Data Required:
| Data Type | Details | Current Source | Status |
|-----------|---------|-----------------|--------|
| **Social Media Sentiment** | Twitter/X, Reddit discussions | Not integrated | ❌ Needs setup |
| **Company Discussions** | Mentions, sentiment from social platforms | Not integrated | ❌ Needs setup |

#### APIs Available:
- **Twitter API v2** (Now X)
  - Endpoint: `https://api.twitter.com/2`
  - Setup: Academic/Enterprise account required
  - Rate Limit: Varies by tier
  - Website: https://developer.twitter.com/en/docs/twitter-api/getting-started/about-twitter-api

- **PRAW (Reddit API)**
  - Endpoint: Python Reddit API Wrapper
  - API Key: Reddit app credentials
  - Rate Limit: Generally permissive
  - Website: https://www.reddit.com/prefs/apps

- **StockTwits API** (Stock sentiment)
  - Endpoint: `https://api.stocktwits.com`
  - No API key required for basic data
  - Website: https://stocktwits.com

---

### 4. **Fundamentals Analyst**
**Purpose**: Financial statement and company health analysis

#### Data Required:
| Data Type | Details | Current Source | Format |
|-----------|---------|-----------------|--------|
| **Balance Sheet** | Assets, Liabilities, Equity | YFinance / Alpha Vantage | Structured data |
| **Income Statement** | Revenue, Expenses, Profit | YFinance / Alpha Vantage | Structured data |
| **Cash Flow** | Operating, Investing, Financing cash flows | YFinance / Alpha Vantage | Structured data |
| **Company Profile** | Sector, Market Cap, Employees | YFinance | Structured data |

#### APIs Available:
- **YFinance (Built-in)** ✅
  - All financial statements included
  - No API key required
  
- **Alpha Vantage (FREE tier available)** ✅
  - Detailed financial statements
  - API Key: Required
  - Rate Limit: 5 req/min (free)
  - Website: https://www.alphavantage.co

- **IEX Cloud** (Premium option)
  - Endpoint: `https://api.iexcloud.io`
  - API Key: Required ($9-$299/month)
  - Data: Real-time financials, company data
  - Website: https://iexcloud.io

---

### 5. **Macro Analyst** (Forex-specific)
**Purpose**: Macroeconomic analysis for currency trading

#### Data Required:
| Data Type | Details | Current Source | Status |
|-----------|---------|-----------------|--------|
| **Interest Rates** | Central bank policy rates | Hardcoded/Demo | ❌ Needs real API |
| **Economic Calendar** | NFP, CPI, GDP, trade data | Hardcoded/Demo | ❌ Needs real API |
| **Central Bank Policy** | Policy statements, guidance | Hardcoded/Demo | ❌ Needs real API |
| **Economic Indicators** | Inflation, employment, GDP | Hardcoded/Demo | ❌ Needs real API |
| **Geopolitical Risk** | Political events, sanctions | N/A | ❌ Needs integration |

#### APIs Available:

**For Central Bank Data:**
- **FRED (Federal Reserve Economic Data)** ✅
  - Endpoint: `https://api.stlouisfed.org/fred`
  - API Key: Free (register at https://fredaccount.stlouisfed.org/login)
  - Data: 500,000+ US economic data series
  - Coverage: USD, inflation, employment, GDP
  - Website: https://fred.stlouisfed.org

- **ECB Statistical Data Warehouse** ✅ 
  - Endpoint: `https://www.ecb.europa.eu/sdw`
  - API: SDMX standard
  - Coverage: EUR economic data
  - Website: https://www.ecb.europa.eu

- **Bank of England API**
  - Endpoint: `https://www.bankofengland.co.uk/boeapidocs`
  - API Key: Free
  - Coverage: GBP economic data
  - Website: https://www.bankofengland.co.uk

**For Economic Calendar:**
- **Trading Economics API** ✅ (RECOMMENDED)
  - Endpoint: `https://tradingeconomics.com/api`
  - API Key: Free tier available
  - Data: Economic calendar, indicators, forecasts
  - Coverage: 200+ countries
  - Website: https://tradingeconomics.com/api

- **Forsights** (Economic calendar)
  - Endpoint: `https://api.forsights.io`
  - API Key: Required
  - Website: https://forsights.io

- **Intrinio** (Premium option)
  - Endpoint: `https://api.intrinio.com`
  - API Key: Required ($249+/month)
  - Website: https://intrinio.com

**For Geopolitical Risk:**
- **GPR Index (Geopolitical Risk Index)**
  - Data: https://www.matteoiacoviello.com/gpr.htm
  - Free download: Historical data available
  - Website: https://www.matteoiacoviello.com

---

### 6. **Forex-Specific Data Sources**

For forex trading, you need currency pair data instead of stock data:

#### Forex Price Data:
| Source | API | Free? | Setup |
|--------|-----|-------|-------|
| **YFinance** | Already integrated | ✅ Yes | Use format: `EURUSD=X` |
| **OANDA** | REST API | ❌ No | Requires account + key |
| **Polygon.io** | `https://api.polygon.io` | Partial | Free tier: restricted |
| **Alpha Vantage** | Already available | ✅ Yes (limited) | API key required |

#### Getting Forex Data from YFinance:
```python
# Correct format for forex pairs in YFinance
symbol = "EURUSD=X"  # EUR/USD
symbol = "GBPUSD=X"  # GBP/USD
symbol = "USDJPY=X"  # USD/JPY

# The "=X" suffix tells YFinance it's forex
```

---

## 🔧 Setting Up Each Data Source

### Alpha Vantage (FREE)

1. **Get API Key**:
   - Visit: https://www.alphavantage.co/api/#api-key
   - Sign up for free
   - Copy your API key

2. **Set Environment Variable**:
   ```bash
   export ALPHA_VANTAGE_API_KEY='your_api_key_here'
   ```

3. **Update Config**:
   ```python
   # tradingagents/default_config.py
   "data_vendors": {
       "core_stock_apis": "alpha_vantage",
       "technical_indicators": "alpha_vantage",
       "fundamental_data": "alpha_vantage",
   }
   ```

### FRED (Federal Reserve)

1. **Get API Key**:
   - Visit: https://fredaccount.stlouisfed.org/login
   - Create account
   - Generate API key

2. **Set Environment Variable**:
   ```bash
   export FRED_API_KEY='your_api_key_here'
   ```

3. **Example Usage**:
   ```python
   import requests
   
   api_key = os.getenv('FRED_API_KEY')
   series_id = 'DFF'  # Federal Funds Rate
   
   url = f'https://api.stlouisfed.org/fred/series/observations'
   params = {
       'series_id': series_id,
       'api_key': api_key,
       'units': 'pch'  # percent change
   }
   
   response = requests.get(url, params=params)
   data = response.json()
   ```

### Trading Economics API

1. **Get API Key**:
   - Visit: https://tradingeconomics.com/api
   - Free tier registration
   - Copy your token

2. **Set Environment Variable**:
   ```bash
   export TRADING_ECONOMICS_API_KEY='your_api_key_here'
   ```

3. **Example Usage**:
   ```python
   import requests
   
   api_key = os.getenv('TRADING_ECONOMICS_API_KEY')
   
   # Get economic calendar
   url = f'https://tradingeconomics.com/api/calendar'
   params = {
       'format': 'json',
       'c': api_key
   }
   
   response = requests.get(url, params=params)
   calendar_events = response.json()
   ```

---

## 📋 Current Implementation Status

### Phase 1: Stock Trading (✅ Working)
- ✅ Market Analyst - using YFinance
- ✅ News Analyst - using YFinance
- ✅ Social Media Analyst - using basic news
- ✅ Fundamentals Analyst - using YFinance

### Phase 2: Forex Trading (⏳ Partial)
- ✅ Macro Analyst created (but data is hardcoded)
- ✅ Forex Market Analyst created
- ❌ Real economic calendar not connected
- ❌ Real interest rate data not connected
- ❌ Real geopolitical data not connected

### Phase 3: Required for Full Forex Support
- [ ] Connect FRED API for interest rates
- [ ] Connect Trading Economics API for calendar
- [ ] Connect ECB API for EUR data
- [ ] Connect Bank of England API for GBP data
- [ ] Integrate geopolitical risk data
- [ ] Fix forex symbol format handling (EURUSD=X)

---

## 🚀 Next Steps

### Immediate (Get forex working):
1. Get FRED API key and integrate interest rates
2. Get Trading Economics API key for economic calendar
3. Fix forex symbol format in YFinance (`EURUSD=X`)
4. Test data retrieval for EURUSD pair

### Short-term (Enhance forex):
1. Add ECB and BoE API integration
2. Implement geopolitical risk scoring
3. Add central bank policy statement parsing

### Long-term (Scale):
1. Add advanced sentiment analysis (Twitter API)
2. Implement real-time data streaming
3. Add custom data provider integrations

---

## 📞 Summary: Where to Get Each API Key

| Service | Website | Free? | Time to Setup |
|---------|---------|-------|----------------|
| Alpha Vantage | https://www.alphavantage.co | Yes | 2 min |
| FRED | https://fredaccount.stlouisfed.org | Yes | 5 min |
| Trading Economics | https://tradingeconomics.com/api | Yes* | 5 min |
| YFinance | Python library | Yes | Installed |
| NewsAPI | https://newsapi.org | Yes* | 3 min |
| IEX Cloud | https://iexcloud.io | No | - |
| ECB API | https://www.ecb.europa.eu | Yes | 0 min |
| OANDA | https://developer.oanda.com | No | - |

*Free tier has limitations (rate limits, historical data)

---

## ⚠️ Important Notes

1. **Rate Limits**: Free APIs have rate limits. For production, consider upgrading to paid tiers.
2. **Data Freshness**: YFinance updates daily after market close. Real-time data requires premium APIs.
3. **Forex Symbols**: YFinance uses `PAIR=X` format (e.g., `EURUSD=X`)
4. **Economic Calendar**: High-impact events are usually released on scheduled dates.
5. **API Keys**: Never commit API keys to git. Use environment variables.


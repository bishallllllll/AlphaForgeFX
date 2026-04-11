"""
Real-time Forex Price Data from Twelve Data
Provides live bid/ask spreads, real-time bars, and tick data for forex pairs
"""

import os
import logging
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from functools import lru_cache

logger = logging.getLogger(__name__)

# Demo data fallback
DEMO_FOREX_PRICES = {
    'EURUSD': {'bid': 1.0850, 'ask': 1.0851, 'spread_pips': 1.0},
    'GBPUSD': {'bid': 1.2680, 'ask': 1.2681, 'spread_pips': 1.0},
    'USDJPY': {'bid': 149.50, 'ask': 149.52, 'spread_pips': 2.0},
    'AUDUSD': {'bid': 0.6650, 'ask': 0.6651, 'spread_pips': 1.0},
}


class TwelveDataForex:
    """Real-time forex price provider using Twelve Data API"""
    
    BASE_URL = "https://api.twelvedata.com"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Twelve Data client
        
        Args:
            api_key: Twelve Data API key (defaults to TWELVE_DATA_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('TWELVE_DATA_API_KEY')
        self.session = requests.Session()
        if self.api_key:
            self.session.params = {'apikey': self.api_key}
    
    def get_price(self, symbol: str, timeout: int = 5) -> Dict:
        """
        Get current forex price with bid/ask
        
        Args:
            symbol: Forex pair (e.g., 'EURUSD', 'EURUSD=FX')
            timeout: Request timeout in seconds
            
        Returns:
            {
                'symbol': 'EURUSD',
                'bid': 1.0850,
                'ask': 1.0851,
                'spread_pips': 1.0,
                'last_update': '2025-04-10T13:30:45Z',
                'source': 'Twelve Data'
            }
        """
        try:
            # Normalize symbol format
            if '=FX' not in symbol:
                symbol_normalized = f"{symbol}=FX"
            else:
                symbol_normalized = symbol
            
            # Build request
            endpoint = f"{self.BASE_URL}/quote"
            params = {
                'symbol': symbol_normalized,
                'format': 'JSON'
            }
            
            # Make request
            response = self.session.get(endpoint, params=params, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data and data['data']:
                quote = data['data']
                bid = float(quote.get('bid', quote.get('last', 0)))
                ask = float(quote.get('ask', quote.get('last', 0)))
                
                # Calculate spread in pips (assuming 4 decimal places for major pairs)
                spread_pips = round((ask - bid) * 10000, 1)
                
                return {
                    'symbol': symbol.replace('=FX', ''),
                    'bid': bid,
                    'ask': ask,
                    'spread_pips': spread_pips,
                    'last_update': datetime.utcnow().isoformat() + 'Z',
                    'source': 'Twelve Data',
                    'status': 'LIVE'
                }
            else:
                logger.warning(f"No data for {symbol}, returning demo data")
                return self._demo_price(symbol)
                
        except Exception as e:
            logger.error(f"Error fetching {symbol} from Twelve Data: {e}")
            return self._demo_price(symbol)
    
    def get_intraday(self, symbol: str, interval: str = '1min', 
                     outputsize: int = 100) -> List[Dict]:
        """
        Get intraday bars for forex pair
        
        Args:
            symbol: Forex pair (e.g., 'EURUSD')
            interval: Bar interval ('1min', '5min', '15min', '1h', '1day')
            outputsize: Number of bars to return (max 5000)
            
        Returns:
            List of OHLCV bars
        """
        try:
            if '=FX' not in symbol:
                symbol_normalized = f"{symbol}=FX"
            else:
                symbol_normalized = symbol
            
            endpoint = f"{self.BASE_URL}/time_series"
            params = {
                'symbol': symbol_normalized,
                'interval': interval,
                'outputsize': outputsize,
                'format': 'JSON'
            }
            
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data:
                return data['data']
            else:
                logger.warning(f"No intraday data for {symbol}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching intraday data for {symbol}: {e}")
            return []
    
    def get_bid_ask_history(self, symbol: str, hours: int = 24) -> Dict:
        """
        Get bid/ask spread history over time
        
        Args:
            symbol: Forex pair
            hours: Historical lookback period
            
        Returns:
            {
                'symbol': 'EURUSD',
                'avg_spread_pips': 1.2,
                'max_spread_pips': 2.1,
                'min_spread_pips': 0.8,
                'volatility': 'NORMAL'
            }
        """
        try:
            bars = self.get_intraday(symbol, interval='1min', outputsize=hours*60)
            
            if not bars:
                return {
                    'symbol': symbol.replace('=FX', ''),
                    'avg_spread_pips': 1.0,
                    'max_spread_pips': 2.0,
                    'min_spread_pips': 0.5,
                    'volatility': 'UNKNOWN'
                }
            
            spreads = []
            for bar in bars[:100]:  # Use last 100 bars for performance
                if 'bid' in bar and 'ask' in bar:
                    bid = float(bar['bid'])
                    ask = float(bar['ask'])
                    spread_pips = round((ask - bid) * 10000, 1)
                    spreads.append(spread_pips)
            
            if not spreads:
                spreads = [1.0]
            
            avg_spread = sum(spreads) / len(spreads)
            max_spread = max(spreads)
            min_spread = min(spreads)
            
            # Volatility assessment
            if avg_spread > 2.0:
                volatility = 'HIGH'
            elif avg_spread > 1.5:
                volatility = 'ELEVATED'
            elif avg_spread < 0.8:
                volatility = 'LOW'
            else:
                volatility = 'NORMAL'
            
            return {
                'symbol': symbol.replace('=FX', ''),
                'avg_spread_pips': round(avg_spread, 2),
                'max_spread_pips': round(max_spread, 2),
                'min_spread_pips': round(min_spread, 2),
                'volatility': volatility
            }
            
        except Exception as e:
            logger.error(f"Error calculating spread history for {symbol}: {e}")
            return {
                'symbol': symbol.replace('=FX', ''),
                'avg_spread_pips': 1.0,
                'volatility': 'UNKNOWN'
            }
    
    @lru_cache(maxsize=32)
    def _demo_price(self, symbol: str) -> Dict:
        """Return demo price data"""
        symbol_clean = symbol.replace('=FX', '')
        if symbol_clean in DEMO_FOREX_PRICES:
            demo = DEMO_FOREX_PRICES[symbol_clean].copy()
            demo['symbol'] = symbol_clean
            demo['last_update'] = datetime.utcnow().isoformat() + 'Z'
            demo['source'] = 'Demo Data'
            demo['status'] = 'DEMO'
            return demo
        
        # Generic demo fallback
        return {
            'symbol': symbol_clean,
            'bid': 1.0000,
            'ask': 1.0001,
            'spread_pips': 1.0,
            'last_update': datetime.utcnow().isoformat() + 'Z',
            'source': 'Demo Data',
            'status': 'DEMO'
        }


# Singleton instance
_forex_client = None


def get_forex_client(api_key: Optional[str] = None) -> TwelveDataForex:
    """Get or create forex client singleton"""
    global _forex_client
    if _forex_client is None:
        _forex_client = TwelveDataForex(api_key)
    return _forex_client


def get_realtime_forex_price(symbol: str) -> Dict:
    """Convenience function to get forex price"""
    client = get_forex_client()
    return client.get_price(symbol)


def get_forex_intraday(symbol: str, interval: str = '5min') -> List[Dict]:
    """Convenience function to get intraday bars"""
    client = get_forex_client()
    return client.get_intraday(symbol, interval=interval)

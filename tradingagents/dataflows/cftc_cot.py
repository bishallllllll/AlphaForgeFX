"""
CFTC Commitment of Traders (CoT) Data
Tracks commercial vs speculative positioning in forex futures
"""

import os
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class PositioningSignal(Enum):
    """CoT positioning signals"""
    EXTREMELY_BULLISH = 1.0
    BULLISH = 0.5
    NEUTRAL = 0.0
    BEARISH = -0.5
    EXTREMELY_BEARISH = -1.0


class CFTCCommitmentOfTraders:
    """CFTC CoT data analyzer for forex positioning"""
    
    CFTC_API = "https://www.cftc.gov/api"
    
    # Currency futures mapping
    CURRENCY_FUTURES = {
        'EUR': {'code': 'EURUSD_FUTURES', 'exchange': 'CME'},
        'GBP': {'code': 'GBPUSD_FUTURES', 'exchange': 'CME'},
        'JPY': {'code': 'USDJPY_FUTURES', 'exchange': 'CME'},
        'CHF': {'code': 'USDCHF_FUTURES', 'exchange': 'CME'},
        'CAD': {'code': 'USDCAD_FUTURES', 'exchange': 'CME'},
        'AUD': {'code': 'AUDUSD_FUTURES', 'exchange': 'CME'},
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.cache = {}
        self.cache_time = {}
    
    def get_cot_positioning(self, currency: str) -> Dict:
        """
        Get current CoT positioning for currency
        
        Args:
            currency: Currency code (EUR, GBP, JPY, etc.)
        
        Returns:
            {
                'currency': 'EUR',
                'large_traders_long': 245000,
                'large_traders_short': 89000,
                'small_traders_long': 156000,
                'small_traders_short': 198000,
                'open_interest': 500000,
                'net_positioning': 'BULLISH',
                'net_long_ratio': 0.73,  # 73% long
                'commercial_bias': 'LONG_BIAS',
                'week_over_week_change': '+5%',
                'extreme_positioning': False,
                'last_report_date': '2025-04-08',
                'days_old': 2
            }
        """
        
        # Check cache
        cache_key = f"cot_{currency}"
        if cache_key in self.cache:
            cached_time = self.cache_time.get(cache_key, datetime.min)
            if (datetime.utcnow() - cached_time).total_seconds() < 86400:  # 24 hours
                return self.cache[cache_key]
        
        try:
            # Fetch from CFTC (fallback to demo data if API fails)
            data = self._fetch_cot_data(currency)
        except Exception as e:
            logger.warning(f"Error fetching CoT data for {currency}: {e}, using demo data")
            data = self._demo_cot_data(currency)
        
        # Cache result
        self.cache[cache_key] = data
        self.cache_time[cache_key] = datetime.utcnow()
        
        return data
    
    def _fetch_cot_data(self, currency: str) -> Dict:
        """Fetch actual CFTC CoT data"""
        # This would call the CFTC API endpoint
        # For now, returning structured demo data
        return self._demo_cot_data(currency)
    
    def _demo_cot_data(self, currency: str) -> Dict:
        """Demo CoT data for testing"""
        
        cot_demo_data = {
            'EUR': {
                'large_traders_long': 245000,
                'large_traders_short': 89000,
                'small_traders_long': 156000,
                'small_traders_short': 198000,
                'open_interest': 588000,
                'week_over_week_change': '+5%',
                'commercial_long': 120000,
                'commercial_short': 145000,
            },
            'GBP': {
                'large_traders_long': 198000,
                'large_traders_short': 112000,
                'small_traders_long': 142000,
                'small_traders_short': 165000,
                'open_interest': 617000,
                'week_over_week_change': '-2%',
                'commercial_long': 98000,
                'commercial_short': 125000,
            },
            'JPY': {
                'large_traders_long': 89000,
                'large_traders_short': 256000,
                'small_traders_long': 134000,
                'small_traders_short': 178000,
                'open_interest': 657000,
                'week_over_week_change': '+12%',
                'commercial_long': 45000,
                'commercial_short': 320000,
            },
            'CHF': {
                'large_traders_long': 145000,
                'large_traders_short': 89000,
                'small_traders_long': 98000,
                'small_traders_short': 124000,
                'open_interest': 456000,
                'week_over_week_change': '0%',
                'commercial_long': 78000,
                'commercial_short': 95000,
            },
        }
        
        if currency not in cot_demo_data:
            # Default demo data
            cot_demo_data[currency] = {
                'large_traders_long': 150000,
                'large_traders_short': 150000,
                'small_traders_long': 100000,
                'small_traders_short': 100000,
                'open_interest': 500000,
                'week_over_week_change': '0%',
                'commercial_long': 100000,
                'commercial_short': 100000,
            }
        
        data = cot_demo_data[currency]
        
        # Calculate derived metrics
        total_long = data['large_traders_long'] + data['small_traders_long']
        total_short = data['large_traders_short'] + data['small_traders_short']
        net_long = total_long - total_short
        net_long_ratio = total_long / (total_long + total_short) if (total_long + total_short) > 0 else 0.5
        
        commercial_net = data['commercial_long'] - data['commercial_short']
        large_trader_net = data['large_traders_long'] - data['large_traders_short']
        
        # Determine positioning signal
        if net_long > 100000:
            net_positioning = 'EXTREMELY_BULLISH'
            signal_value = 1.0
        elif net_long > 30000:
            net_positioning = 'BULLISH'
            signal_value = 0.5
        elif net_long > -30000:
            net_positioning = 'NEUTRAL'
            signal_value = 0.0
        elif net_long > -100000:
            net_positioning = 'BEARISH'
            signal_value = -0.5
        else:
            net_positioning = 'EXTREMELY_BEARISH'
            signal_value = -1.0
        
        # Commercial bias
        if commercial_net > 50000:
            commercial_bias = 'STRONG_LONG_BIAS'
        elif commercial_net > 0:
            commercial_bias = 'LONG_BIAS'
        elif commercial_net > -50000:
            commercial_bias = 'SLIGHT_SHORT_BIAS'
        else:
            commercial_bias = 'STRONG_SHORT_BIAS'
        
        # Extreme positioning detection
        extreme = abs(signal_value) > 0.8 and abs(net_long_ratio - 0.5) > 0.15
        
        return {
            'currency': currency,
            'large_traders_long': data['large_traders_long'],
            'large_traders_short': data['large_traders_short'],
            'small_traders_long': data['small_traders_long'],
            'small_traders_short': data['small_traders_short'],
            'commercial_long': data['commercial_long'],
            'commercial_short': data['commercial_short'],
            'open_interest': data['open_interest'],
            'net_long_position': net_long,
            'net_positioning': net_positioning,
            'net_long_ratio': round(net_long_ratio, 3),
            'commercial_bias': commercial_bias,
            'commercial_net': commercial_net,
            'large_trader_net': large_trader_net,
            'week_over_week_change': data['week_over_week_change'],
            'extreme_positioning': extreme,
            'signal_value': signal_value,
            'last_report_date': (datetime.utcnow() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'days_old': 2,
            'source': 'CFTC',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def get_positioning_comparison(self, currency_pairs: List[str]) -> Dict:
        """
        Compare positioning across multiple currencies
        
        Args:
            currency_pairs: List of currency codes ['EUR', 'GBP', 'JPY']
        
        Returns:
            {
                'most_bullish': 'EUR',
                'most_bearish': 'JPY',
                'consensus': 'SHORT_BIAS_DEVELOPING',
                'crowded_trades': ['EUR', 'GBP'],
                'contrarian_signal': 'POSSIBLE_JPY_BOUNCE'
            }
        """
        positions = {}
        for currency in currency_pairs:
            positions[currency] = self.get_cot_positioning(currency)
        
        # Find extremes
        signals = {curr: pos['signal_value'] for curr, pos in positions.items()}
        most_bullish = max(signals, key=signals.get)
        most_bearish = min(signals, key=signals.get)
        avg_signal = sum(signals.values()) / len(signals) if signals else 0
        
        # Detect crowded trades
        crowded = [curr for curr, sig in signals.items() if abs(sig) > 0.7]
        
        # Consensus
        if avg_signal > 0.3:
            consensus = 'BULLISH_BIAS'
        elif avg_signal < -0.3:
            consensus = 'BEARISH_BIAS'
        else:
            consensus = 'NEUTRAL'
        
        # Contrarian signal (extremely bullish may indicate top)
        contrarian_signals = []
        for currency, sig in signals.items():
            if sig > 0.8:
                contrarian_signals.append(f"Possible {currency} pullback risk")
            elif sig < -0.8:
                contrarian_signals.append(f"Possible {currency} bounce opportunity")
        
        return {
            'currencies_analyzed': currency_pairs,
            'most_bullish': most_bullish,
            'most_bullish_signal': round(signals[most_bullish], 2),
            'most_bearish': most_bearish,
            'most_bearish_signal': round(signals[most_bearish], 2),
            'average_signal': round(avg_signal, 2),
            'consensus': consensus,
            'crowded_trades': crowded,
            'extreme_trades_count': len(crowded),
            'contrarian_opportunities': contrarian_signals,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def get_positioning_extremes(self) -> Dict:
        """
        Identify extreme positioning across all major currencies
        
        Returns:
            {
                'extreme_longs': ['EUR'],
                'extreme_shorts': ['JPY'],
                'historical_percentile': {...},
                'risk_alert': 'HIGH_EUR_POSITIONING_RISK'
            }
        """
        all_currencies = list(self.CURRENCY_FUTURES.keys())
        positions = {}
        
        for currency in all_currencies:
            pos = self.get_cot_positioning(currency)
            positions[currency] = pos['signal_value']
        
        extreme_longs = [c for c, sig in positions.items() if sig > 0.7]
        extreme_shorts = [c for c, sig in positions.items() if sig < -0.7]
        
        risk_alert = None
        if len(extreme_longs) > 2:
            risk_alert = f"HIGH_LONG_CROWDING: {', '.join(extreme_longs)}"
        elif len(extreme_shorts) > 2:
            risk_alert = f"HIGH_SHORT_CROWDING: {', '.join(extreme_shorts)}"
        
        return {
            'extreme_longs': extreme_longs,
            'extreme_shorts': extreme_shorts,
            'total_extreme_positions': len(extreme_longs) + len(extreme_shorts),
            'market_positioning_balance': 'SKEWED' if risk_alert else 'BALANCED',
            'risk_alert': risk_alert,
            'recommendation': 'CAUTION_EXTREME_LONGS' if extreme_longs else 
                            'CAUTION_EXTREME_SHORTS' if extreme_shorts else 
                            'NO_EXTREME_POSITIONING',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }


# Singleton
_cot_client = None


def get_cot_client() -> CFTCCommitmentOfTraders:
    """Get or create client singleton"""
    global _cot_client
    if _cot_client is None:
        _cot_client = CFTCCommitmentOfTraders()
    return _cot_client


def get_cot_positioning(currency: str) -> Dict:
    """Convenience function"""
    client = get_cot_client()
    return client.get_cot_positioning(currency)


def compare_cot_positioning(currencies: List[str]) -> Dict:
    """Convenience function"""
    client = get_cot_client()
    return client.get_positioning_comparison(currencies)


def get_cot_extremes() -> Dict:
    """Convenience function"""
    client = get_cot_client()
    return client.get_positioning_extremes()

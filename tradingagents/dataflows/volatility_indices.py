"""
Volatility Indices (VIX, MOVE, TYVIX)
Tracks market fear and risk appetite across asset classes
"""

import os
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

import requests

logger = logging.getLogger(__name__)


class VolatilityLevel(Enum):
    """Volatility assessment levels."""

    VERY_LOW = 1
    LOW = 2
    NORMAL = 3
    ELEVATED = 4
    HIGH = 5
    EXTREME = 6


class VolatilityIndices:
    """Volatility index provider for VIX, MOVE, TYVIX"""
    
    # Yahoo Finance endpoints (free)
    YAHOO_FINANCE_API = "https://query1.finance.yahoo.com/v8/finance/chart"
    
    # Symbols for volatility indices
    SYMBOLS = {
        'VIX': '^VIX',           # S&P 500 implied volatility
        'MOVE': '^MOVE',         # Bond market volatility
        'TYVIX': '^TYVIX',       # 10Y Treasury volatility
        'OVX': '^OVX',           # Oil volatility
        'GVZ': '^GVZ',           # Gold volatility
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.cache = {}
        self.cache_time = {}
    
    def get_vix(self) -> Dict:
        """
        Get VIX (S&P 500 implied volatility)
        
        Returns:
            {
                'index': 'VIX',
                'value': 18.5,
                'level': 'NORMAL',
                'interpretation': 'Low fear, risk-on sentiment',
                'term_structure': 'BACKWARDATION',
                '1d_change': -1.2,
                'status': 'LIVE'
            }
        """
        try:
            # Try to fetch live data
            data = self._fetch_vix_yahoo()
            if data:
                return data
        except Exception as e:
            logger.warning(f"Error fetching VIX: {e}, using demo data")
        
        return self._demo_vix()
    
    def get_move_index(self) -> Dict:
        """
        Get MOVE Index (Bond market volatility)
        
        Returns:
            {
                'index': 'MOVE',
                'value': 121.3,
                'level': 'ELEVATED',
                'interpretation': 'Bond investors pricing in rate volatility',
                'components': {...}
            }
        """
        try:
            data = self._fetch_move_yahoo()
            if data:
                return data
        except Exception as e:
            logger.warning(f"Error fetching MOVE: {e}, using demo data")
        
        return self._demo_move()
    
    def get_all_volatility_indices(self) -> Dict:
        """
        Get all major volatility indices
        
        Returns:
            {
                'vix': {...},
                'move': {...},
                'tyvix': {...},
                'ovx': {...},
                'gvz': {...},
                'risk_sentiment': 'RISK_ON',
                'volatility_regime': 'NORMAL_VOLATILITY'
            }
        """
        vix = self.get_vix()
        move = self.get_move_index()
        tyvix = self.get_tyvix()
        ovx = self.get_ovx()
        gvz = self.get_gvz()
        
        # Assess overall risk sentiment
        vix_level = vix['level_numeric']
        move_level = move['level_numeric']
        tyvix_level = tyvix['level_numeric']
        
        avg_vol_level = (vix_level + move_level + tyvix_level) / 3
        
        if avg_vol_level < 2.5:
            risk_sentiment = 'RISK_ON'
            regime = 'LOW_VOLATILITY'
        elif avg_vol_level < 3.5:
            risk_sentiment = 'NEUTRAL'
            regime = 'NORMAL_VOLATILITY'
        elif avg_vol_level < 4.5:
            risk_sentiment = 'RISK_OFF'
            regime = 'ELEVATED_VOLATILITY'
        else:
            risk_sentiment = 'EXTREME_RISK_OFF'
            regime = 'HIGH_VOLATILITY'
        
        return {
            'vix': vix,
            'move': move,
            'tyvix': tyvix,
            'ovx': ovx,
            'gvz': gvz,
            'risk_sentiment': risk_sentiment,
            'volatility_regime': regime,
            'correlation_vix_move': 0.65,  # Typical correlation
            'inflation_volatility_spike': False,
            'equity_bond_divergence': False,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def get_tyvix(self) -> Dict:
        """Get 10Y Treasury volatility"""
        try:
            data = self._fetch_tyvix_yahoo()
            if data:
                return data
        except:
            pass
        
        return self._demo_tyvix()
    
    def get_ovx(self) -> Dict:
        """Get Oil volatility index"""
        return self._demo_ovx()
    
    def get_gvz(self) -> Dict:
        """Get Gold volatility index"""
        return self._demo_gvz()
    
    def _fetch_vix_yahoo(self) -> Optional[Dict]:
        """Fetch VIX from Yahoo Finance"""
        try:
            params = {'interval': '1d', 'range': '1d'}
            response = self.session.get(
                f"{self.YAHOO_FINANCE_API}/^VIX",
                params=params,
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart']:
                result = data['chart']['result'][0]
                if result['meta']:
                    price = result['meta'].get('regularMarketPrice', 18.5)
                    
                    return {
                        'index': 'VIX',
                        'value': round(price, 2),
                        'level': self._assess_vix_level(price),
                        'level_numeric': self._vix_level_numeric(price),
                        'interpretation': self._vix_interpretation(price),
                        '1d_change': -0.5,
                        'source': 'Yahoo Finance',
                        'status': 'LIVE',
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    }
        except Exception as e:
            logger.debug(f"Yahoo fetch failed: {e}")
        
        return None
    
    def _fetch_move_yahoo(self) -> Optional[Dict]:
        """Fetch MOVE from Yahoo Finance"""
        try:
            params = {'interval': '1d', 'range': '1d'}
            response = self.session.get(
                f"{self.YAHOO_FINANCE_API}/^MOVE",
                params=params,
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart']:
                result = data['chart']['result'][0]
                if result['meta']:
                    price = result['meta'].get('regularMarketPrice', 121.3)
                    
                    return {
                        'index': 'MOVE',
                        'value': round(price, 2),
                        'level': self._assess_move_level(price),
                        'level_numeric': self._move_level_numeric(price),
                        'interpretation': self._move_interpretation(price),
                        'source': 'Yahoo Finance',
                        'status': 'LIVE',
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    }
        except:
            pass
        
        return None
    
    def _fetch_tyvix_yahoo(self) -> Optional[Dict]:
        """Fetch TYVIX from Yahoo Finance"""
        try:
            params = {'interval': '1d', 'range': '1d'}
            response = self.session.get(
                f"{self.YAHOO_FINANCE_API}/^TYVIX",
                params=params,
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart']:
                result = data['chart']['result'][0]
                if result['meta']:
                    price = result['meta'].get('regularMarketPrice', 95.0)
                    return {
                        'index': 'TYVIX',
                        'value': round(price, 2),
                        'level': self._assess_tyvix_level(price),
                        'level_numeric': self._tyvix_level_numeric(price),
                        'source': 'Yahoo Finance',
                        'status': 'LIVE'
                    }
        except:
            pass
        
        return None
    
    def _demo_vix(self) -> Dict:
        """Demo VIX data"""
        return {
            'index': 'VIX',
            'value': 18.5,
            'level': 'NORMAL',
            'level_numeric': 3,
            'interpretation': 'Low fear, risk-on sentiment persisting',
            'historical_average': 19.2,
            '1d_change': -1.2,
            '5d_change': -2.5,
            'source': 'Demo Data',
            'status': 'DEMO',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def _demo_move(self) -> Dict:
        """Demo MOVE data"""
        return {
            'index': 'MOVE',
            'value': 121.3,
            'level': 'ELEVATED',
            'level_numeric': 4,
            'interpretation': 'Bond investors pricing in rate volatility',
            'historical_average': 115.0,
            '1d_change': 1.8,
            'source': 'Demo Data',
            'status': 'DEMO',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def _demo_tyvix(self) -> Dict:
        """Demo TYVIX data"""
        return {
            'index': 'TYVIX',
            'value': 95.0,
            'level': 'NORMAL',
            'level_numeric': 3,
            'source': 'Demo Data',
            'status': 'DEMO',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def _demo_ovx(self) -> Dict:
        """Demo OVX data"""
        return {
            'index': 'OVX',
            'value': 28.5,
            'level': 'LOW',
            'source': 'Demo Data',
            'status': 'DEMO',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def _demo_gvz(self) -> Dict:
        """Demo GVZ data"""
        return {
            'index': 'GVZ',
            'value': 15.2,
            'level': 'VERY_LOW',
            'source': 'Demo Data',
            'status': 'DEMO',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def _assess_vix_level(self, value: float) -> str:
        """Assess VIX level"""
        if value < 12:
            return 'VERY_LOW'
        elif value < 16:
            return 'LOW'
        elif value < 20:
            return 'NORMAL'
        elif value < 30:
            return 'ELEVATED'
        elif value < 40:
            return 'HIGH'
        else:
            return 'EXTREME'
    
    def _vix_level_numeric(self, value: float) -> int:
        """VIX level as numeric"""
        level = self._assess_vix_level(value)
        return {
            'VERY_LOW': 1, 'LOW': 2, 'NORMAL': 3,
            'ELEVATED': 4, 'HIGH': 5, 'EXTREME': 6
        }[level]
    
    def _vix_interpretation(self, value: float) -> str:
        """VIX interpretation"""
        level = self._assess_vix_level(value)
        interpretations = {
            'VERY_LOW': 'Complacency, possible market top risk',
            'LOW': 'Low fear, risk-on sentiment',
            'NORMAL': 'Normal market anxiety',
            'ELEVATED': 'Elevated uncertainty, investors cautious',
            'HIGH': 'High fear, risk-off sentiment',
            'EXTREME': 'Panic selling, potential capitulation'
        }
        return interpretations.get(level, 'Unknown')
    
    def _assess_move_level(self, value: float) -> str:
        """Assess MOVE level"""
        if value < 90:
            return 'LOW'
        elif value < 110:
            return 'NORMAL'
        elif value < 130:
            return 'ELEVATED'
        elif value < 150:
            return 'HIGH'
        else:
            return 'EXTREME'
    
    def _move_level_numeric(self, value: float) -> int:
        """MOVE level as numeric"""
        level = self._assess_move_level(value)
        return {'LOW': 2, 'NORMAL': 3, 'ELEVATED': 4, 'HIGH': 5, 'EXTREME': 6}[level]
    
    def _move_interpretation(self, value: float) -> str:
        """MOVE interpretation"""
        level = self._assess_move_level(value)
        interpretations = {
            'LOW': 'Stable rates, low bond volatility',
            'NORMAL': 'Normal rate volatility',
            'ELEVATED': 'Elevated rate volatility, policy uncertainty',
            'HIGH': 'High rate volatility, FX swings likely',
            'EXTREME': 'Extreme rate volatility, potential crisis'
        }
        return interpretations.get(level, 'Unknown')
    
    def _assess_tyvix_level(self, value: float) -> str:
        """Assess TYVIX level"""
        if value < 70:
            return 'LOW'
        elif value < 100:
            return 'NORMAL'
        elif value < 130:
            return 'ELEVATED'
        else:
            return 'HIGH'
    
    def _tyvix_level_numeric(self, value: float) -> int:
        """TYVIX level as numeric"""
        level = self._assess_tyvix_level(value)
        return {'LOW': 2, 'NORMAL': 3, 'ELEVATED': 4, 'HIGH': 5}[level]


# Singleton
_vol_client = None


def get_volatility_client() -> VolatilityIndices:
    """Get or create client singleton"""
    global _vol_client
    if _vol_client is None:
        _vol_client = VolatilityIndices()
    return _vol_client


def get_vix() -> Dict:
    """Convenience function"""
    client = get_volatility_client()
    return client.get_vix()


def get_move() -> Dict:
    """Convenience function"""
    client = get_volatility_client()
    return client.get_move_index()


def get_all_volatility() -> Dict:
    """Convenience function"""
    client = get_volatility_client()
    return client.get_all_volatility_indices()

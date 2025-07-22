import logging
import time
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional, Tuple, Union
import ta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scanner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """Technical analysis calculations with proper Series handling"""
    
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI with proper Series handling"""
        return ta.momentum.RSIIndicator(close=data, window=period).rsi()
    
    @staticmethod
    def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate ADX with proper Series handling"""
        return ta.trend.ADXIndicator(high=high, low=low, close=close, window=period).adx()
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, period: int = 20, std: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands with proper Series handling"""
        bb_indicator = ta.volatility.BollingerBands(close=data, window=period, window_dev=std)
        return bb_indicator.bollinger_mavg(), bb_indicator.bollinger_hband(), bb_indicator.bollinger_lband()
    
    @staticmethod
    def calculate_sma(data: pd.Series, period: int = 20) -> pd.Series:
        """Calculate Simple Moving Average"""
        return ta.trend.SMAIndicator(close=data, window=period).sma_indicator()

class SignalEvaluator:
    """Signal evaluation with proper pandas Series boolean handling"""
    
    def __init__(self):
        self.analyzer = TechnicalAnalyzer()
    
    def evaluate_signals(self, symbol: str, timeframe: str = "5m") -> Optional[Dict]:
        """
        Evaluate trading signals for a given symbol with proper Series handling
        
        This addresses the error: "The truth value of a Series is ambiguous"
        by using proper pandas methods like .any(), .all(), .empty, .bool(), .item()
        """
        try:
            # Fetch data
            ticker = yf.Ticker(symbol)
            
            # Get period based on timeframe
            period_map = {
                "5m": "5d",  # 5 days of 5-minute data
                "1h": "1mo", # 1 month of hourly data
                "1d": "1y"   # 1 year of daily data
            }
            
            data = ticker.history(period=period_map.get(timeframe, "5d"), interval=timeframe)
            
            if data.empty:
                logger.warning(f"No data available for {symbol}")
                return None
            
            # Calculate indicators
            close = data['Close']
            high = data['High']
            low = data['Low']
            
            rsi = self.analyzer.calculate_rsi(close)
            adx = self.analyzer.calculate_adx(high, low, close)
            sma20 = self.analyzer.calculate_sma(close, 20)
            bb_middle, bb_upper, bb_lower = self.analyzer.calculate_bollinger_bands(close)
            
            # Get latest values using .iloc[-1] to avoid Series ambiguity
            current_price = close.iloc[-1] if not close.empty else None
            current_rsi = rsi.iloc[-1] if not rsi.empty else None
            current_adx = adx.iloc[-1] if not adx.empty else None
            current_sma20 = sma20.iloc[-1] if not sma20.empty else None
            current_bb_upper = bb_upper.iloc[-1] if not bb_upper.empty else None
            current_bb_lower = bb_lower.iloc[-1] if not bb_lower.empty else None
            
            if any(val is None or pd.isna(val) for val in [current_price, current_rsi, current_adx, current_sma20, current_bb_upper, current_bb_lower]):
                logger.warning(f"Insufficient indicator data for {symbol}")
                return None
            
            # Evaluate signals with proper boolean handling
            signals = []
            score = 0
            
            # RSI oversold condition (proper boolean evaluation)
            if current_rsi < 30:
                signals.append("RSI Oversold")
                score += 1
            elif current_rsi > 70:
                signals.append("RSI Overbought")  
                score += 1
            
            # Strong trend condition
            if current_adx > 25:
                signals.append(f"Strong trend (ADX: {current_adx:.1f})")
                score += 1
            
            # Bollinger Band breakout
            if current_price < current_bb_lower:
                signals.append(f"Price below BB ({current_price:.4f} < {current_bb_lower:.4f})")
                score += 1
            elif current_price > current_bb_upper:
                signals.append(f"Price above BB ({current_price:.4f} > {current_bb_upper:.4f})")
                score += 1
            
            # Trend direction
            trend = "WZROSTOWY" if current_price > current_sma20 else "SPADKOWY"
            
            if score >= 2:  # Alert threshold
                return {
                    'symbol': symbol,
                    'score': score,
                    'price': current_price,
                    'rsi': current_rsi,
                    'adx': current_adx,
                    'sma20': current_sma20,
                    'signals': signals,
                    'trend': trend,
                    'timeframe': timeframe
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Błąd oceny sygnałów dla {symbol}: {str(e)}")
            return None

class TelegramNotifier:
    """Telegram notification system"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    def send_alert(self, alert_data: Dict) -> bool:
        """Send alert to Telegram with proper HTML formatting"""
        try:
            # Create message with proper HTML formatting
            symbol_name = {
                'NG=F': 'Gaz naturalny',
                'CL=F': 'Ropa naftowa', 
                'GC=F': 'Złoto'
            }.get(alert_data['symbol'], alert_data['symbol'])
            
            message = f"""🚨 <b>ALERT: {symbol_name} ({alert_data['timeframe']})</b> - Score: {alert_data['score']}

💰 <b>Cena:</b> {alert_data['price']:.4f}
📊 <b>RSI:</b> {alert_data['rsi']:.1f}, <b>ADX:</b> {alert_data['adx']:.1f}

"""
            
            for signal in alert_data['signals']:
                message += f"✓ {signal}\n"
            
            message += f"\n📈 <b>Trend:</b> {alert_data['trend']} (SMA20: {alert_data['sma20']:.4f})"
            
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(self.api_url, data=payload, timeout=10)
            response_data = response.json()
            
            if response_data.get('ok'):
                logger.info("   📱 Wysłano na Telegram")
                return True
            else:
                logger.error(f"Telegram API error: {response_data}")
                logger.error("   ❌ Błąd wysyłania na Telegram")
                return False
                
        except Exception as e:
            logger.error(f"Telegram error: {str(e)}")
            logger.error("   ❌ Błąd wysyłania na Telegram")
            return False

class GasScanner:
    """Main gas prediction scanner"""
    
    def __init__(self, telegram_token: str = "", telegram_chat_id: str = ""):
        self.evaluator = SignalEvaluator()
        self.telegram = TelegramNotifier(telegram_token, telegram_chat_id) if telegram_token and telegram_chat_id else None
        self.symbols = ['NG=F', 'CL=F', 'GC=F']  # Natural Gas, Crude Oil, Gold
        self.scan_count = 0
        
    def run_scan(self) -> int:
        """Run a single scan and return number of alerts"""
        self.scan_count += 1
        start_time = time.time()
        
        logger.info("=" * 50)
        logger.info(f"🔍 Skan #{self.scan_count} o {datetime.now().strftime('%H:%M:%S')}")
        
        alerts_count = 0
        
        for symbol in self.symbols:
            alert = self.evaluator.evaluate_signals(symbol, "5m")
            
            if alert:
                alerts_count += 1
                
                # Log alert
                symbol_name = {
                    'NG=F': 'Gaz',
                    'CL=F': 'Ropa', 
                    'GC=F': 'Złoto'
                }.get(symbol, symbol)
                
                logger.info(f"🚨 ALERT: {symbol_name} (5m) - Score: {alert['score']}")
                logger.info(f"   💰 Cena: {alert['price']:.4f}")
                logger.info(f"   📊 RSI: {alert['rsi']:.1f}, ADX: {alert['adx']:.1f}")
                
                for signal in alert['signals']:
                    logger.info(f"   ✓ {signal}")
                
                logger.info(f"   📈 Trend: {alert['trend']} (SMA20: {alert['sma20']:.4f})")
                
                # Send to Telegram
                if self.telegram:
                    self.telegram.send_alert(alert)
        
        elapsed = time.time() - start_time
        logger.info(f"✅ Skan zakończony w {elapsed:.1f}s - {alerts_count} alertów")
        
        return alerts_count
    
    def start_scanning(self, interval_seconds: int = 60):
        """Start continuous scanning"""
        logger.info("🚀 Uruchamianie skanera gazu...")
        logger.info(f"📊 Symbole: {', '.join(self.symbols)}")
        logger.info(f"⏰ Interwał: {interval_seconds}s")
        
        try:
            while True:
                self.run_scan()
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            logger.info("\n👋 Skaner zatrzymany przez użytkownika")
        except Exception as e:
            logger.error(f"Błąd skanera: {str(e)}")

def main():
    """Main entry point"""
    # You can set your Telegram credentials here
    TELEGRAM_BOT_TOKEN = ""  # Set your bot token
    TELEGRAM_CHAT_ID = ""    # Set your chat ID
    
    scanner = GasScanner(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    scanner.start_scanning(interval_seconds=60)

if __name__ == "__main__":
    main()
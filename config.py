# Configuration file for the gas prediction scanner

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = ""  # Your Telegram bot token
TELEGRAM_CHAT_ID = ""    # Your Telegram chat ID

# Scanner Settings
SCAN_INTERVAL = 60  # seconds between scans
ALERT_THRESHOLD = 2  # minimum score for alert

# Technical Analysis Settings
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

ADX_PERIOD = 14
ADX_THRESHOLD = 25  # minimum for strong trend

BOLLINGER_PERIOD = 20
BOLLINGER_STD = 2.0

SMA_PERIOD = 20

# Symbols to scan
SYMBOLS = [
    'NG=F',  # Natural Gas
    'CL=F',  # Crude Oil  
    'GC=F'   # Gold
]

# Timeframes
TIMEFRAMES = {
    "5m": "5d",   # 5 days of 5-minute data
    "1h": "1mo",  # 1 month of hourly data
    "1d": "1y"    # 1 year of daily data
}

DEFAULT_TIMEFRAME = "5m"
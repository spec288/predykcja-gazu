# Gas Prediction Scanner

A Python application for scanning gas and commodity futures data to generate trading alerts based on technical analysis.

## Problem Solved

This application addresses the common pandas error:
```
The truth value of a Series is ambiguous. Use a.empty, a.bool(), a.item(), a.any() or a.all().
```

## Features

- **Technical Analysis**: RSI, ADX, Bollinger Bands, SMA calculations
- **Signal Evaluation**: Automated signal detection with proper pandas Series handling
- **Telegram Notifications**: Optional alert system via Telegram bot
- **Multi-Symbol Scanning**: Supports Natural Gas (NG=F), Crude Oil (CL=F), Gold (GC=F)
- **Robust Error Handling**: Proper pandas Series boolean operations

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Configure Telegram notifications in `config.py`:
```python
TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"
```

## Usage

### Basic Usage
```bash
python scanner.py
```

### Running Tests
```bash
python test_scanner.py
```

## Key Technical Fixes

### 1. Proper Series Boolean Handling
Instead of direct boolean evaluation of Series:
```python
# ❌ This causes "Series is ambiguous" error
if some_series:
    do_something()

# ✅ Correct approach
if not some_series.empty:
    latest_value = some_series.iloc[-1]
    if latest_value > threshold:
        do_something()
```

### 2. Safe Series Comparisons
```python
# ✅ Use proper pandas methods
comparison_result = series > threshold
if comparison_result.any():  # or .all()
    handle_condition()

# ✅ For single values
if not series.empty:
    single_value = series.iloc[-1]  # or .item() for single-element Series
```

### 3. Technical Indicator Processing
```python
# ✅ Safe indicator value extraction
current_rsi = rsi.iloc[-1] if not rsi.empty else None
if current_rsi is not None and not pd.isna(current_rsi):
    # Process indicator
```

## File Structure

- `scanner.py` - Main application
- `config.py` - Configuration settings
- `test_scanner.py` - Test suite
- `requirements.txt` - Python dependencies

## Technical Indicators

- **RSI (Relative Strength Index)**: Momentum oscillator (14-period)
- **ADX (Average Directional Index)**: Trend strength indicator (14-period)
- **Bollinger Bands**: Volatility indicator (20-period, 2 std dev)
- **SMA (Simple Moving Average)**: Trend indicator (20-period)

## Alert Conditions

Alerts are generated when score ≥ 2 based on:
- RSI oversold/overbought conditions
- Strong trend (ADX > 25)
- Bollinger Band breakouts
- Price vs SMA trend direction

## Logging

The application logs all operations to:
- Console output
- `scanner.log` file

## Error Handling

- Network connectivity issues
- Data availability problems  
- Series boolean evaluation errors
- Telegram API failures

All errors are logged without crashing the application.
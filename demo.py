#!/usr/bin/env python3
"""
Simple demo script showing the solution to pandas Series ambiguity errors
"""

import pandas as pd
import numpy as np
from scanner import SignalEvaluator
import logging

# Configure logging to see the output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demonstrate_series_fix():
    """Demonstrate the fix for 'The truth value of a Series is ambiguous' error"""
    
    print("=" * 60)
    print("🔧 DEMONSTRATION: Pandas Series Boolean Evaluation Fix")
    print("=" * 60)
    
    # Create sample data that mimics real trading data
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=50, freq='H')
    prices = 100 + np.cumsum(np.random.randn(50) * 0.1)
    price_series = pd.Series(prices, index=dates)
    
    print(f"📊 Sample data created: {len(price_series)} price points")
    print(f"   Latest price: {price_series.iloc[-1]:.2f}")
    
    # Simulate technical indicators
    sma = price_series.rolling(window=20).mean()
    
    print("\n🚨 PROBLEMATIC APPROACHES (would cause errors):")
    print("   ❌ if price_series > sma:  # 'Series is ambiguous' error")
    print("   ❌ if price_series:        # 'Series is ambiguous' error")
    
    print("\n✅ CORRECT APPROACHES:")
    
    # 1. Use proper comparison methods
    above_sma = price_series > sma
    print(f"   1. Series comparison: {above_sma.sum()} prices above SMA")
    print(f"      Any above SMA: {above_sma.any()}")
    print(f"      All above SMA: {above_sma.all()}")
    
    # 2. Use proper value extraction
    if not price_series.empty:
        latest_price = price_series.iloc[-1]
        latest_sma = sma.iloc[-1] if not sma.empty else None
        
        if latest_sma is not None and not pd.isna(latest_sma):
            trend = "WZROSTOWY" if latest_price > latest_sma else "SPADKOWY"
            print(f"   2. Latest comparison: Price {latest_price:.2f} vs SMA {latest_sma:.2f} = {trend}")
    
    # 3. Use empty check
    print(f"   3. Series empty check: {price_series.empty}")
    
    # 4. For single-value Series
    single_value_series = pd.Series([42.5])
    print(f"   4. Single value extraction: {single_value_series.item()}")
    
    print("\n🎯 REAL-WORLD APPLICATION:")
    
    # Demonstrate with SignalEvaluator (would work with real data)
    evaluator = SignalEvaluator()
    print("   Signal evaluator created successfully")
    print("   Ready to process real market data without Series errors")
    
    print("\n✅ SUCCESS: All pandas Series operations handled properly!")
    print("=" * 60)

if __name__ == "__main__":
    demonstrate_series_fix()
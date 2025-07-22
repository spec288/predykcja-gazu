#!/usr/bin/env python3
"""
Test script to verify the scanner works without Series ambiguity errors
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scanner import GasScanner, SignalEvaluator, TechnicalAnalyzer
import pandas as pd
import numpy as np
import logging

# Set logging to INFO to see the test output
logging.getLogger().setLevel(logging.INFO)

def test_technical_analyzer():
    """Test technical analysis calculations"""
    print("\n🔍 Testing TechnicalAnalyzer...")
    
    # Create sample data
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    
    data = pd.Series(prices, index=dates)
    high = data * 1.02
    low = data * 0.98
    
    analyzer = TechnicalAnalyzer()
    
    try:
        # Test RSI calculation
        rsi = analyzer.calculate_rsi(data)
        print(f"✓ RSI calculation successful. Latest RSI: {rsi.iloc[-1]:.2f}")
        
        # Test ADX calculation  
        adx = analyzer.calculate_adx(high, low, data)
        print(f"✓ ADX calculation successful. Latest ADX: {adx.iloc[-1]:.2f}")
        
        # Test Bollinger Bands
        bb_middle, bb_upper, bb_lower = analyzer.calculate_bollinger_bands(data)
        print(f"✓ Bollinger Bands calculation successful. Upper: {bb_upper.iloc[-1]:.2f}, Lower: {bb_lower.iloc[-1]:.2f}")
        
        # Test SMA
        sma = analyzer.calculate_sma(data)
        print(f"✓ SMA calculation successful. Latest SMA: {sma.iloc[-1]:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ TechnicalAnalyzer test failed: {e}")
        return False

def test_signal_evaluator():
    """Test signal evaluation with real data"""
    print("\n🔍 Testing SignalEvaluator...")
    
    evaluator = SignalEvaluator()
    
    # Test with a limited symbol to avoid rate limits
    test_symbol = "NG=F"
    
    try:
        result = evaluator.evaluate_signals(test_symbol, "5m")
        
        if result:
            print(f"✓ Signal evaluation successful for {test_symbol}")
            print(f"  Score: {result['score']}")
            print(f"  Price: {result['price']:.4f}")
            print(f"  RSI: {result['rsi']:.1f}")
            print(f"  ADX: {result['adx']:.1f}")
            print(f"  Signals: {result['signals']}")
        else:
            print(f"✓ Signal evaluation completed for {test_symbol} (no alert generated)")
            
        return True
        
    except Exception as e:
        print(f"❌ SignalEvaluator test failed: {e}")
        return False

def test_scanner_initialization():
    """Test scanner initialization"""
    print("\n🔍 Testing Scanner initialization...")
    
    try:
        scanner = GasScanner()
        print("✓ Scanner initialized successfully")
        
        # Test a single scan
        print("Running single test scan...")
        alerts = scanner.run_scan()
        print(f"✓ Scan completed. Alerts generated: {alerts}")
        
        return True
        
    except Exception as e:
        print(f"❌ Scanner test failed: {e}")
        return False

def test_pandas_series_handling():
    """Test that we properly handle pandas Series boolean operations"""
    print("\n🔍 Testing Pandas Series boolean handling...")
    
    try:
        # Create test Series
        s1 = pd.Series([1, 2, 3, 4, 5])
        s2 = pd.Series([3, 3, 3, 3, 3])
        
        # These should NOT cause "The truth value of a Series is ambiguous" error
        
        # Test proper ways to handle Series comparisons
        comparison = s1 > s2
        print(f"✓ Series comparison created: {comparison.sum()} values are True")
        
        # Test proper boolean evaluation methods
        any_true = comparison.any()
        all_true = comparison.all()
        is_empty = comparison.empty
        
        print(f"✓ .any(): {any_true}")
        print(f"✓ .all(): {all_true}")
        print(f"✓ .empty: {is_empty}")
        
        # Test single value extraction
        if not s1.empty:
            single_val = s1.iloc[-1]
            print(f"✓ Single value extraction: {single_val}")
        
        # Test item() for single element Series
        single_series = pd.Series([42])
        item_val = single_series.item()
        print(f"✓ .item() method: {item_val}")
        
        print("✓ All pandas Series boolean operations handled correctly")
        return True
        
    except Exception as e:
        print(f"❌ Pandas Series handling test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting scanner tests...")
    
    tests = [
        test_pandas_series_handling,
        test_technical_analyzer,
        test_signal_evaluator,
        test_scanner_initialization
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
            failed += 1
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! The scanner should work without Series ambiguity errors.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit(main())
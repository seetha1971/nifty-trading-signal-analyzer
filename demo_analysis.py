"""
Demo script to test the multi-stock analysis functionality
"""

import pandas as pd
from datetime import datetime
import time

# Import our modules
from nifty50_stocks import get_top_fno_stocks
from multi_stock_fetcher import fetch_nifty50_data
from multi_stock_analyzer import analyze_multiple_stocks, create_signals_summary

def run_demo():
    """Run a demo analysis on a small subset of stocks."""
    
    print("🚀 Nifty 50 FNO Trading Signal Analyzer Demo")
    print("=" * 50)
    
    # Configuration
    num_stocks = 10  # Start with 10 stocks for demo
    period = "1mo"
    interval = "1d"  # Use daily data for faster demo
    
    print(f"📊 Analyzing top {num_stocks} stocks...")
    print(f"📅 Period: {period}, Interval: {interval}")
    print()
    
    # Step 1: Fetch data
    print("📈 Fetching stock data...")
    start_time = time.time()
    
    stock_data = fetch_nifty50_data(period=period, interval=interval, top_n=num_stocks)
    
    fetch_time = time.time() - start_time
    print(f"✅ Fetched data for {len(stock_data)} stocks in {fetch_time:.2f} seconds")
    print()
    
    # Step 2: Analyze signals
    print("🔍 Analyzing trading signals...")
    start_time = time.time()
    
    analysis_results = analyze_multiple_stocks(
        stock_data,
        doji_threshold=0.1,
        mfi_oversold=30,
        mfi_overbought=70
    )
    
    analysis_time = time.time() - start_time
    print(f"✅ Analysis complete in {analysis_time:.2f} seconds")
    print()
    
    # Step 3: Display results
    print("📋 Signal Summary:")
    print("-" * 30)
    
    signal_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0, 'ERROR': 0}
    
    for stock, result in analysis_results.items():
        if 'error' in result:
            print(f"❌ {stock}: Error - {result['error']}")
            signal_counts['ERROR'] += 1
        elif result['latest_signal'] is not None:
            signal = result['latest_signal']['signal']
            strength = abs(result['latest_signal']['strength'])
            price = result['latest_signal']['close_price']
            mfi = result['latest_signal']['mfi']
            
            signal_icon = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '⚫'}[signal]
            print(f"{signal_icon} {stock}: {signal} (Strength: {strength}) - ₹{price:.2f} | MFI: {mfi:.1f}")
            signal_counts[signal] += 1
    
    print()
    print("📊 Portfolio Summary:")
    print("-" * 20)
    for signal_type, count in signal_counts.items():
        if count > 0:
            print(f"{signal_type}: {count}")
    
    # Step 4: Show top signals
    signals_df = create_signals_summary(analysis_results)
    
    if not signals_df.empty:
        print()
        print("🎯 Top BUY Signals:")
        print("-" * 18)
        buy_signals = signals_df[signals_df['Signal'] == 'BUY'].head(3)
        for _, row in buy_signals.iterrows():
            print(f"• {row['Stock']}: Strength {row['Strength']}, Price ₹{row['Price']}")
        
        print()
        print("🎯 Top SELL Signals:")
        print("-" * 19)
        sell_signals = signals_df[signals_df['Signal'] == 'SELL'].head(3)
        for _, row in sell_signals.iterrows():
            print(f"• {row['Stock']}: Strength {row['Strength']}, Price ₹{row['Price']}")
    
    print()
    print("✨ Demo completed successfully!")
    print(f"⏱️  Total execution time: {fetch_time + analysis_time:.2f} seconds")

if __name__ == "__main__":
    try:
        run_demo()
    except Exception as e:
        print(f"❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
"""
Simple test script for multi-stock analysis without Streamlit dependencies
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
from trading_indicators import calculate_all_indicators

def test_single_stock():
    """Test analysis on a single stock"""
    print("🧪 Testing single stock analysis...")
    
    # Fetch TCS data
    ticker = yf.Ticker("TCS.NS")
    data = ticker.history(period="1mo", interval="1d")
    
    if data.empty:
        print("❌ No data fetched")
        return
    
    # Prepare data
    data.reset_index(inplace=True)
    
    print(f"Data columns: {list(data.columns)}")
    print(f"Data shape: {data.shape}")
    
    # Remove unnecessary columns
    cols_to_remove = ['Dividends', 'Stock Splits', 'Adj Close']
    for col in cols_to_remove:
        if col in data.columns:
            data = data.drop(col, axis=1)
    
    # Rename Date to Datetime if needed
    if 'Date' in data.columns:
        data = data.rename(columns={'Date': 'Datetime'})
    
    # Ensure required columns exist
    required_cols = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']
    
    if not all(col in data.columns for col in required_cols):
        missing = [col for col in required_cols if col not in data.columns]
        print(f"❌ Missing columns: {missing}")
        return False
    
    print(f"✅ Fetched {len(data)} data points for TCS")
    print(f"Date range: {data['Datetime'].min()} to {data['Datetime'].max()}")
    
    # Calculate indicators
    try:
        result = calculate_all_indicators(data)
        
        # Get latest signal
        if not result.empty:
            latest = result.iloc[-1]
            print(f"\n📊 Latest Analysis for TCS:")
            print(f"Signal: {latest['Signal']}")
            print(f"Strength: {latest['Signal_Strength']}")
            print(f"Price: ₹{latest['Close']:.2f}")
            print(f"MFI: {latest['MFI']:.1f}")
            print(f"MACD: {latest['MACD']:.4f}")
            print(f"Is Doji: {latest['Is_Doji']}")
            print(f"Reason: {latest['Signal_Reason']}")
            
            # Count signals
            total_signals = len(result[result['Signal'] != 'HOLD'])
            buy_signals = len(result[result['Signal'] == 'BUY'])
            sell_signals = len(result[result['Signal'] == 'SELL'])
            doji_count = len(result[result['Is_Doji']])
            
            print(f"\n📈 Statistics:")
            print(f"Total data points: {len(result)}")
            print(f"Total signals: {total_signals}")
            print(f"Buy signals: {buy_signals}")
            print(f"Sell signals: {sell_signals}")
            print(f"Doji patterns: {doji_count}")
            
            return True
        else:
            print("❌ No analysis results")
            return False
            
    except Exception as e:
        print(f"❌ Error in analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_stocks():
    """Test analysis on multiple stocks"""
    print("\n🧪 Testing multiple stocks analysis...")
    
    stocks = ['TCS.NS', 'INFY.NS', 'RELIANCE.NS']
    results = {}
    
    for stock in stocks:
        try:
            ticker = yf.Ticker(stock)
            data = ticker.history(period="1mo", interval="1d")
            
            if not data.empty:
                # Prepare data
                data.reset_index(inplace=True)
                
                # Remove unnecessary columns
                cols_to_remove = ['Dividends', 'Stock Splits', 'Adj Close']
                for col in cols_to_remove:
                    if col in data.columns:
                        data = data.drop(col, axis=1)
                
                # Rename Date to Datetime if needed
                if 'Date' in data.columns:
                    data = data.rename(columns={'Date': 'Datetime'})
                
                # Analyze
                analysis_result = calculate_all_indicators(data)
                
                if not analysis_result.empty:
                    latest = analysis_result.iloc[-1]
                    results[stock.replace('.NS', '')] = {
                        'signal': latest['Signal'],
                        'strength': latest['Signal_Strength'],
                        'price': latest['Close'],
                        'mfi': latest['MFI'],
                        'is_doji': latest['Is_Doji']
                    }
                    print(f"✅ {stock.replace('.NS', '')}: {latest['Signal']} (Strength: {abs(latest['Signal_Strength'])})")
                else:
                    print(f"❌ {stock.replace('.NS', '')}: No analysis results")
            else:
                print(f"❌ {stock.replace('.NS', '')}: No data")
                
        except Exception as e:
            print(f"❌ {stock.replace('.NS', '')}: Error - {str(e)}")
    
    # Summary
    if results:
        print(f"\n📊 Summary for {len(results)} stocks:")
        buy_count = sum(1 for r in results.values() if r['signal'] == 'BUY')
        sell_count = sum(1 for r in results.values() if r['signal'] == 'SELL')
        hold_count = sum(1 for r in results.values() if r['signal'] == 'HOLD')
        
        print(f"BUY signals: {buy_count}")
        print(f"SELL signals: {sell_count}")
        print(f"HOLD: {hold_count}")
        
        return True
    
    return False

if __name__ == "__main__":
    print("🚀 Testing Nifty 50 FNO Trading Signal Analyzer")
    print("=" * 50)
    
    success = True
    
    # Test single stock
    success &= test_single_stock()
    
    # Test multiple stocks
    success &= test_multiple_stocks()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
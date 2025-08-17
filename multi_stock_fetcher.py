"""
Multi Stock Data Fetcher Module
Handles fetching data for multiple stocks concurrently and efficiently.
"""

import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from nifty50_stocks import get_nifty50_stocks, get_top_fno_stocks

def fetch_single_stock_data(stock_symbol: str, period: str = "1mo", interval: str = "15m") -> Optional[pd.DataFrame]:
    """
    Fetch data for a single stock.
    
    Args:
        stock_symbol: Yahoo Finance symbol (e.g., 'TCS.NS')
        period: Data period
        interval: Data interval
        
    Returns:
        DataFrame with OHLC and Volume data, or None if error
    """
    try:
        ticker = yf.Ticker(stock_symbol)
        data = ticker.history(period=period, interval=interval)
        
        if data.empty:
            return None
        
        # Reset index to make datetime a column
        data.reset_index(inplace=True)
        
        # Standardize column names based on actual columns
        if len(data.columns) == 6:
            data.columns = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']
        elif len(data.columns) == 7:
            data.columns = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
            data = data.drop('Adj Close', axis=1)
        else:
            # Handle other cases
            required_cols = ['Open', 'High', 'Low', 'Close']
            if all(col in data.columns for col in required_cols):
                if 'Volume' not in data.columns:
                    data['Volume'] = 1000000
                # Rename Datetime column if it exists
                if 'Date' in data.columns:
                    data['Datetime'] = data['Date']
                elif data.index.name == 'Date' or data.index.name == 'Datetime':
                    data['Datetime'] = data.index
            else:
                return None
        
        # Add stock symbol for identification
        data['Symbol'] = stock_symbol.replace('.NS', '')
        
        # Remove any rows with missing data
        data.dropna(inplace=True)
        
        # Ensure we have volume data
        if 'Volume' not in data.columns or data['Volume'].isna().all():
            data['Volume'] = 1000000  # Default volume
        
        return data
        
    except Exception as e:
        print(f"Error fetching data for {stock_symbol}: {str(e)}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_multiple_stocks_data(
    stock_symbols: List[str], 
    period: str = "1mo", 
    interval: str = "15m",
    max_workers: int = 10
) -> Dict[str, pd.DataFrame]:
    """
    Fetch data for multiple stocks concurrently.
    
    Args:
        stock_symbols: List of Yahoo Finance symbols
        period: Data period
        interval: Data interval
        max_workers: Maximum number of concurrent workers
        
    Returns:
        Dictionary with stock symbols as keys and DataFrames as values
    """
    results = {}
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_symbol = {
            executor.submit(fetch_single_stock_data, symbol, period, interval): symbol
            for symbol in stock_symbols
        }
        
        completed = 0
        total = len(stock_symbols)
        
        # Process completed tasks
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            
            try:
                data = future.result()
                if data is not None:
                    stock_name = symbol.replace('.NS', '')
                    results[stock_name] = data
                    status_text.text(f"✅ Fetched data for {stock_name}")
                else:
                    status_text.text(f"❌ Failed to fetch data for {symbol.replace('.NS', '')}")
            except Exception as e:
                status_text.text(f"❌ Error with {symbol.replace('.NS', '')}: {str(e)}")
            
            completed += 1
            progress_bar.progress(completed / total)
            time.sleep(0.1)  # Small delay to show progress
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    return results

def fetch_nifty50_data(period: str = "1mo", interval: str = "15m", top_n: int = 50) -> Dict[str, pd.DataFrame]:
    """
    Fetch data for top N Nifty 50 FNO stocks.
    
    Args:
        period: Data period
        interval: Data interval
        top_n: Number of top stocks to fetch
        
    Returns:
        Dictionary with stock data
    """
    stocks = get_top_fno_stocks(top_n)
    stock_symbols = list(stocks.values())
    
    return fetch_multiple_stocks_data(stock_symbols, period, interval)

def combine_stock_data(stock_data_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Combine multiple stock DataFrames into a single DataFrame.
    
    Args:
        stock_data_dict: Dictionary of stock DataFrames
        
    Returns:
        Combined DataFrame with all stocks
    """
    all_data = []
    
    for stock_symbol, data in stock_data_dict.items():
        if data is not None and not data.empty:
            data_copy = data.copy()
            data_copy['Stock'] = stock_symbol
            all_data.append(data_copy)
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        return combined_df.sort_values(['Stock', 'Datetime']).reset_index(drop=True)
    
    return pd.DataFrame()

def get_stock_summary(stock_data_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Create a summary DataFrame with latest information for all stocks.
    
    Args:
        stock_data_dict: Dictionary of stock DataFrames
        
    Returns:
        Summary DataFrame
    """
    summary_data = []
    
    for stock_symbol, data in stock_data_dict.items():
        if data is not None and not data.empty:
            latest = data.iloc[-1]
            previous = data.iloc[-2] if len(data) > 1 else latest
            
            change = latest['Close'] - previous['Close']
            change_percent = (change / previous['Close']) * 100 if previous['Close'] != 0 else 0
            
            summary_data.append({
                'Stock': stock_symbol,
                'Close': latest['Close'],
                'Open': latest['Open'],
                'High': latest['High'],
                'Low': latest['Low'],
                'Volume': latest['Volume'],
                'Change': change,
                'Change%': change_percent,
                'Last_Updated': latest['Datetime']
            })
    
    if summary_data:
        df = pd.DataFrame(summary_data)
        return df.sort_values('Change%', ascending=False).reset_index(drop=True)
    
    return pd.DataFrame()

def validate_stock_data(stock_data_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Validate and clean stock data.
    
    Args:
        stock_data_dict: Dictionary of stock DataFrames
        
    Returns:
        Validated stock data dictionary
    """
    validated_data = {}
    
    for stock_symbol, data in stock_data_dict.items():
        if data is not None and not data.empty:
            # Check if we have minimum required data points
            if len(data) >= 20:  # Minimum 20 data points for indicators
                # Ensure all required columns exist
                required_cols = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']
                if all(col in data.columns for col in required_cols):
                    validated_data[stock_symbol] = data
    
    return validated_data
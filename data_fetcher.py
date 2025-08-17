"""
Data Fetcher Module
Handles fetching NIFTY data from Yahoo Finance and data preprocessing.
"""

import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_nifty_data(period: str = "1mo", interval: str = "15m") -> Optional[pd.DataFrame]:
    """
    Fetch NIFTY data from Yahoo Finance.
    
    Args:
        period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
    Returns:
        DataFrame with OHLC and Volume data, or None if error
    """
    try:
        # Fetch NIFTY 50 data (^NSEI is the Yahoo Finance symbol for NIFTY 50)
        ticker = yf.Ticker("^NSEI")
        data = ticker.history(period=period, interval=interval)
        
        if data.empty:
            st.error("No data retrieved. Please check your connection or try a different time period.")
            return None
        
        # Reset index to make datetime a column
        data.reset_index(inplace=True)
        
        # Rename columns to match our indicator functions
        data.columns = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']
        
        # Remove any rows with missing data
        data.dropna(inplace=True)
        
        # Ensure we have volume data (some intervals might not have volume)
        if 'Volume' not in data.columns or data['Volume'].isna().all():
            # If no volume data, create dummy volume data
            data['Volume'] = 1000000  # Set a default volume
        
        return data
        
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None


def get_available_periods() -> dict:
    """
    Get available period options for data fetching.
    
    Returns:
        Dictionary mapping display names to yfinance period codes
    """
    return {
        "1 Day": "1d",
        "5 Days": "5d", 
        "1 Month": "1mo",
        "3 Months": "3mo",
        "6 Months": "6mo",
        "1 Year": "1y",
        "2 Years": "2y"
    }


def get_available_intervals() -> dict:
    """
    Get available interval options for data fetching.
    
    Returns:
        Dictionary mapping display names to yfinance interval codes
    """
    return {
        "1 Minute": "1m",
        "2 Minutes": "2m", 
        "5 Minutes": "5m",
        "15 Minutes": "15m",
        "30 Minutes": "30m",
        "1 Hour": "1h",
        "1 Day": "1d"
    }


def validate_period_interval_combination(period: str, interval: str) -> bool:
    """
    Validate if the period and interval combination is supported by Yahoo Finance.
    
    Args:
        period: Period string
        interval: Interval string
        
    Returns:
        Boolean indicating if combination is valid
    """
    # Yahoo Finance has restrictions on period-interval combinations
    interval_restrictions = {
        "1m": ["1d", "5d"],
        "2m": ["1d", "5d"], 
        "5m": ["1d", "5d"],
        "15m": ["1d", "5d", "1mo"],
        "30m": ["1d", "5d", "1mo"],
        "1h": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"],
        "1d": ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
    }
    
    if interval in interval_restrictions:
        return period in interval_restrictions[interval]
    
    return True  # Default to True for unlisted combinations


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the fetched data for analysis.
    
    Args:
        df: Raw data from Yahoo Finance
        
    Returns:
        Preprocessed DataFrame
    """
    # Make a copy to avoid modifying original data
    processed_df = df.copy()
    
    # Sort by datetime to ensure proper chronological order
    processed_df = processed_df.sort_values('Datetime')
    
    # Reset index
    processed_df.reset_index(drop=True, inplace=True)
    
    # Ensure all price columns are numeric
    price_columns = ['Open', 'High', 'Low', 'Close']
    for col in price_columns:
        processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce')
    
    # Ensure volume is numeric
    processed_df['Volume'] = pd.to_numeric(processed_df['Volume'], errors='coerce')
    
    # Fill any remaining NaN values with forward fill
    processed_df.fillna(method='ffill', inplace=True)
    
    # Drop any rows that still have NaN values
    processed_df.dropna(inplace=True)
    
    return processed_df


def get_latest_price_info(df: pd.DataFrame) -> dict:
    """
    Get latest price information from the dataframe.
    
    Args:
        df: DataFrame with OHLC data
        
    Returns:
        Dictionary with latest price information
    """
    if df.empty:
        return {}
    
    latest = df.iloc[-1]
    previous = df.iloc[-2] if len(df) > 1 else latest
    
    change = latest['Close'] - previous['Close']
    change_percent = (change / previous['Close']) * 100
    
    return {
        'datetime': latest['Datetime'],
        'close': latest['Close'],
        'open': latest['Open'],
        'high': latest['High'],
        'low': latest['Low'],
        'volume': latest['Volume'],
        'change': change,
        'change_percent': change_percent,
        'previous_close': previous['Close']
    }
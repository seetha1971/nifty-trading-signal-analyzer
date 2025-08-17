"""
Trading Indicators Module
Contains functions for calculating technical indicators used in the NIFTY trading signal analyzer.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any


def calculate_heikinashi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Heikin-Ashi candles from regular OHLC data.
    
    Args:
        df: DataFrame with OHLC data (Open, High, Low, Close columns)
        
    Returns:
        DataFrame with Heikin-Ashi OHLC values
    """
    ha_df = df.copy()
    
    # Calculate Heikin-Ashi values
    ha_df['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
    
    # Initialize first HA_Open
    ha_df.loc[ha_df.index[0], 'HA_Open'] = (df.loc[df.index[0], 'Open'] + df.loc[df.index[0], 'Close']) / 2
    
    # Calculate subsequent HA_Open values
    for i in range(1, len(ha_df)):
        ha_df.loc[ha_df.index[i], 'HA_Open'] = (
            ha_df.loc[ha_df.index[i-1], 'HA_Open'] + ha_df.loc[ha_df.index[i-1], 'HA_Close']
        ) / 2
    
    # Calculate HA_High and HA_Low
    ha_df['HA_High'] = ha_df[['High', 'HA_Open', 'HA_Close']].max(axis=1)
    ha_df['HA_Low'] = ha_df[['Low', 'HA_Open', 'HA_Close']].min(axis=1)
    
    return ha_df


def detect_doji_candles(df: pd.DataFrame, doji_threshold: float = 0.1) -> pd.Series:
    """
    Detect Doji candles in Heikin-Ashi data.
    
    Args:
        df: DataFrame with Heikin-Ashi OHLC data
        doji_threshold: Threshold for body size relative to high-low range
        
    Returns:
        Boolean Series indicating Doji candles
    """
    # Calculate body and shadow sizes
    body_size = abs(df['HA_Close'] - df['HA_Open'])
    total_range = df['HA_High'] - df['HA_Low']
    
    # Avoid division by zero
    body_ratio = np.where(total_range != 0, body_size / total_range, 0)
    
    # A Doji has a very small body relative to its total range
    is_doji = body_ratio <= doji_threshold
    
    return pd.Series(is_doji, index=df.index, name='Is_Doji')


def calculate_mfi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Money Flow Index (MFI).
    
    Args:
        df: DataFrame with OHLC and Volume data
        period: Period for MFI calculation
        
    Returns:
        Series with MFI values
    """
    # Calculate typical price
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    
    # Calculate money flow
    money_flow = typical_price * df['Volume']
    
    # Calculate positive and negative money flow
    price_change = typical_price.diff()
    
    positive_flow = pd.Series(0.0, index=df.index)
    negative_flow = pd.Series(0.0, index=df.index)
    
    positive_mask = price_change > 0
    negative_mask = price_change < 0
    
    positive_flow[positive_mask] = money_flow[positive_mask]
    negative_flow[negative_mask] = money_flow[negative_mask]
    
    # Calculate money flow ratio and MFI
    positive_flow_sum = positive_flow.rolling(window=period).sum()
    negative_flow_sum = negative_flow.rolling(window=period).sum()
    
    # Avoid division by zero
    money_ratio = np.where(negative_flow_sum != 0, 
                          positive_flow_sum / negative_flow_sum, 
                          100.0)
    
    mfi = 100 - (100 / (1 + money_ratio))
    
    return pd.Series(mfi, index=df.index, name='MFI')


def calculate_macd(df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence) indicator.
    
    Args:
        df: DataFrame with Close price data
        fast_period: Period for fast EMA
        slow_period: Period for slow EMA
        signal_period: Period for signal line EMA
        
    Returns:
        Dictionary with MACD line, signal line, and histogram
    """
    # Calculate EMAs
    ema_fast = df['Close'].ewm(span=fast_period).mean()
    ema_slow = df['Close'].ewm(span=slow_period).mean()
    
    # Calculate MACD line
    macd_line = ema_fast - ema_slow
    
    # Calculate signal line
    signal_line = macd_line.ewm(span=signal_period).mean()
    
    # Calculate MACD histogram
    macd_histogram = macd_line - signal_line
    
    return {
        'MACD': macd_line,
        'MACD_Signal': signal_line,
        'MACD_Histogram': macd_histogram
    }


def detect_macd_crossovers(macd_data: Dict[str, pd.Series]) -> Dict[str, pd.Series]:
    """
    Detect MACD crossovers (bullish and bearish signals).
    
    Args:
        macd_data: Dictionary with MACD, signal line, and histogram data
        
    Returns:
        Dictionary with bullish and bearish crossover signals
    """
    macd = macd_data['MACD']
    signal = macd_data['MACD_Signal']
    
    # Detect crossovers - handle NaN values
    macd_above_signal = (macd > signal).fillna(False)
    macd_above_signal_prev = macd_above_signal.shift(1).fillna(False)
    
    # Bullish crossover: MACD crosses above signal line
    bullish_crossover = (~macd_above_signal_prev) & macd_above_signal
    
    # Bearish crossover: MACD crosses below signal line  
    bearish_crossover = macd_above_signal_prev & (~macd_above_signal)
    
    return {
        'MACD_Bullish': bullish_crossover.fillna(False),
        'MACD_Bearish': bearish_crossover.fillna(False)
    }


def generate_trading_signals(df: pd.DataFrame, mfi_oversold: int = 30, mfi_overbought: int = 70) -> pd.DataFrame:
    """
    Generate comprehensive trading signals based on Heikin-Ashi Doji, MFI, and MACD.
    
    Args:
        df: DataFrame with complete OHLC, Volume, and calculated indicators
        mfi_oversold: MFI level considered oversold
        mfi_overbought: MFI level considered overbought
        
    Returns:
        DataFrame with trading signals
    """
    signals_df = df.copy()
    
    # Initialize signal columns
    signals_df['Signal'] = 'HOLD'
    signals_df['Signal_Strength'] = 0
    signals_df['Signal_Reason'] = ''
    
    # Define conditions
    doji_condition = signals_df['Is_Doji']
    mfi_oversold_condition = signals_df['MFI'] < mfi_oversold
    mfi_overbought_condition = signals_df['MFI'] > mfi_overbought
    macd_bullish = signals_df['MACD_Bullish']
    macd_bearish = signals_df['MACD_Bearish']
    
    # Generate BUY signals
    buy_conditions = []
    buy_reasons = []
    buy_strengths = []
    
    # Strong BUY: Doji + Oversold MFI + MACD Bullish crossover
    strong_buy = doji_condition & mfi_oversold_condition & macd_bullish
    buy_conditions.append(strong_buy)
    buy_reasons.append('Doji + Oversold MFI + MACD Bullish')
    buy_strengths.append(3)
    
    # Medium BUY: Doji + Oversold MFI
    medium_buy_1 = doji_condition & mfi_oversold_condition & ~macd_bullish
    buy_conditions.append(medium_buy_1)
    buy_reasons.append('Doji + Oversold MFI')
    buy_strengths.append(2)
    
    # Medium BUY: Doji + MACD Bullish
    medium_buy_2 = doji_condition & macd_bullish & ~mfi_oversold_condition
    buy_conditions.append(medium_buy_2)
    buy_reasons.append('Doji + MACD Bullish')
    buy_strengths.append(2)
    
    # Weak BUY: Just oversold MFI + MACD Bullish
    weak_buy = ~doji_condition & mfi_oversold_condition & macd_bullish
    buy_conditions.append(weak_buy)
    buy_reasons.append('Oversold MFI + MACD Bullish')
    buy_strengths.append(1)
    
    # Generate SELL signals
    sell_conditions = []
    sell_reasons = []
    sell_strengths = []
    
    # Strong SELL: Doji + Overbought MFI + MACD Bearish crossover
    strong_sell = doji_condition & mfi_overbought_condition & macd_bearish
    sell_conditions.append(strong_sell)
    sell_reasons.append('Doji + Overbought MFI + MACD Bearish')
    sell_strengths.append(-3)
    
    # Medium SELL: Doji + Overbought MFI
    medium_sell_1 = doji_condition & mfi_overbought_condition & ~macd_bearish
    sell_conditions.append(medium_sell_1)
    sell_reasons.append('Doji + Overbought MFI')
    sell_strengths.append(-2)
    
    # Medium SELL: Doji + MACD Bearish
    medium_sell_2 = doji_condition & macd_bearish & ~mfi_overbought_condition
    sell_conditions.append(medium_sell_2)
    sell_reasons.append('Doji + MACD Bearish')
    sell_strengths.append(-2)
    
    # Weak SELL: Just overbought MFI + MACD Bearish
    weak_sell = ~doji_condition & mfi_overbought_condition & macd_bearish
    sell_conditions.append(weak_sell)
    sell_reasons.append('Overbought MFI + MACD Bearish')
    sell_strengths.append(-1)
    
    # Apply BUY signals (prioritize stronger signals)
    for condition, reason, strength in zip(buy_conditions, buy_reasons, buy_strengths):
        mask = condition & (signals_df['Signal_Strength'] < strength)
        signals_df.loc[mask, 'Signal'] = 'BUY'
        signals_df.loc[mask, 'Signal_Strength'] = strength
        signals_df.loc[mask, 'Signal_Reason'] = reason
    
    # Apply SELL signals (prioritize stronger signals)
    for condition, reason, strength in zip(sell_conditions, sell_reasons, sell_strengths):
        mask = condition & (signals_df['Signal_Strength'] > strength)
        signals_df.loc[mask, 'Signal'] = 'SELL'
        signals_df.loc[mask, 'Signal_Strength'] = strength
        signals_df.loc[mask, 'Signal_Reason'] = reason
    
    return signals_df


def calculate_all_indicators(df: pd.DataFrame, doji_threshold: float = 0.1, mfi_oversold: int = 30, mfi_overbought: int = 70) -> pd.DataFrame:
    """
    Calculate all trading indicators for the given OHLC data.
    
    Args:
        df: DataFrame with OHLC and Volume data
        doji_threshold: Threshold for Doji detection
        mfi_oversold: MFI oversold level
        mfi_overbought: MFI overbought level
        
    Returns:
        DataFrame with all calculated indicators and signals
    """
    # Calculate Heikin-Ashi
    ha_df = calculate_heikinashi(df)
    
    # Detect Doji candles
    ha_df['Is_Doji'] = detect_doji_candles(ha_df, doji_threshold)
    
    # Calculate MFI
    ha_df['MFI'] = calculate_mfi(df)
    
    # Calculate MACD
    macd_data = calculate_macd(df)
    ha_df['MACD'] = macd_data['MACD']
    ha_df['MACD_Signal'] = macd_data['MACD_Signal']
    ha_df['MACD_Histogram'] = macd_data['MACD_Histogram']
    
    # Detect MACD crossovers
    macd_crossovers = detect_macd_crossovers(macd_data)
    ha_df['MACD_Bullish'] = macd_crossovers['MACD_Bullish']
    ha_df['MACD_Bearish'] = macd_crossovers['MACD_Bearish']
    
    # Generate trading signals
    result_df = generate_trading_signals(ha_df, mfi_oversold, mfi_overbought)
    
    return result_df
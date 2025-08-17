"""
Multi Stock Trading Signal Analyzer
Analyzes multiple stocks for trading signals using Heikin Ashi Doji, MACD, and MFI.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st

from trading_indicators import calculate_all_indicators

def analyze_single_stock(
    stock_symbol: str, 
    data: pd.DataFrame,
    doji_threshold: float = 0.1,
    mfi_oversold: int = 30,
    mfi_overbought: int = 70
) -> Dict:
    """
    Analyze a single stock for trading signals.
    
    Args:
        stock_symbol: Stock symbol
        data: OHLC data for the stock
        doji_threshold: Doji detection threshold
        mfi_oversold: MFI oversold level
        mfi_overbought: MFI overbought level
        
    Returns:
        Dictionary with analysis results
    """
    try:
        # Calculate all indicators and signals
        df = calculate_all_indicators(data.copy(), doji_threshold, mfi_oversold, mfi_overbought)
        
        # Get latest signal
        if not df.empty:
            latest = df.iloc[-1]
            
            # Calculate signal statistics
            total_signals = len(df[df['Signal'] != 'HOLD'])
            buy_signals = len(df[df['Signal'] == 'BUY'])
            sell_signals = len(df[df['Signal'] == 'SELL'])
            doji_count = len(df[df['Is_Doji']])
            
            # Signal strength distribution
            signal_strengths = df[df['Signal'] != 'HOLD']['Signal_Strength'].abs()
            avg_signal_strength = signal_strengths.mean() if len(signal_strengths) > 0 else 0
            
            return {
                'stock': stock_symbol,
                'data': df,
                'latest_signal': {
                    'signal': latest['Signal'],
                    'strength': latest['Signal_Strength'],
                    'reason': latest['Signal_Reason'],
                    'close_price': latest['Close'],
                    'ha_close': latest['HA_Close'],
                    'macd': latest.get('MACD', 0),
                    'macd_signal': latest.get('MACD_Signal', 0),
                    'mfi': latest.get('MFI', 50),
                    'is_doji': latest['Is_Doji'],
                    'datetime': latest['Datetime']
                },
                'statistics': {
                    'total_signals': total_signals,
                    'buy_signals': buy_signals,
                    'sell_signals': sell_signals,
                    'signal_rate': (total_signals / len(df)) * 100,
                    'buy_rate': (buy_signals / total_signals) * 100 if total_signals > 0 else 0,
                    'sell_rate': (sell_signals / total_signals) * 100 if total_signals > 0 else 0,
                    'doji_count': doji_count,
                    'doji_rate': (doji_count / len(df)) * 100,
                    'avg_signal_strength': avg_signal_strength,
                    'data_points': len(df)
                }
            }
    except Exception as e:
        return {
            'stock': stock_symbol,
            'error': str(e),
            'data': pd.DataFrame(),
            'latest_signal': None,
            'statistics': {}
        }

def analyze_multiple_stocks(
    stock_data_dict: Dict[str, pd.DataFrame],
    doji_threshold: float = 0.1,
    mfi_oversold: int = 30,
    mfi_overbought: int = 70,
    max_workers: int = 10
) -> Dict[str, Dict]:
    """
    Analyze multiple stocks concurrently.
    
    Args:
        stock_data_dict: Dictionary of stock data
        doji_threshold: Doji detection threshold
        mfi_oversold: MFI oversold level
        mfi_overbought: MFI overbought level
        max_workers: Maximum concurrent workers
        
    Returns:
        Dictionary with analysis results for each stock
    """
    results = {}
    
    # Create progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit analysis tasks
        future_to_stock = {
            executor.submit(
                analyze_single_stock, 
                stock_symbol, 
                data, 
                doji_threshold, 
                mfi_oversold, 
                mfi_overbought
            ): stock_symbol
            for stock_symbol, data in stock_data_dict.items()
        }
        
        completed = 0
        total = len(stock_data_dict)
        
        # Process completed analyses
        for future in as_completed(future_to_stock):
            stock_symbol = future_to_stock[future]
            
            try:
                result = future.result()
                results[stock_symbol] = result
                
                if 'error' in result:
                    status_text.text(f"❌ Error analyzing {stock_symbol}: {result['error']}")
                else:
                    signal = result['latest_signal']['signal']
                    status_text.text(f"✅ {stock_symbol}: {signal}")
                    
            except Exception as e:
                results[stock_symbol] = {
                    'stock': stock_symbol,
                    'error': str(e),
                    'data': pd.DataFrame(),
                    'latest_signal': None,
                    'statistics': {}
                }
                status_text.text(f"❌ Exception analyzing {stock_symbol}: {str(e)}")
            
            completed += 1
            progress_bar.progress(completed / total)
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    return results

def create_signals_summary(analysis_results: Dict[str, Dict]) -> pd.DataFrame:
    """
    Create a summary DataFrame of all stock signals.
    
    Args:
        analysis_results: Dictionary of analysis results
        
    Returns:
        DataFrame with signal summary
    """
    summary_data = []
    
    for stock_symbol, result in analysis_results.items():
        if 'error' not in result and result['latest_signal'] is not None:
            latest = result['latest_signal']
            stats = result['statistics']
            
            summary_data.append({
                'Stock': stock_symbol,
                'Signal': latest['signal'],
                'Strength': abs(latest['strength']),
                'Price': latest['close_price'],
                'MACD': latest['macd'],
                'MFI': latest['mfi'],
                'Is_Doji': latest['is_doji'],
                'Total_Signals': stats['total_signals'],
                'Signal_Rate%': round(stats['signal_rate'], 1),
                'Buy_Rate%': round(stats['buy_rate'], 1),
                'Sell_Rate%': round(stats['sell_rate'], 1),
                'Doji_Rate%': round(stats['doji_rate'], 1),
                'Avg_Strength': round(stats['avg_signal_strength'], 2),
                'Reason': latest['reason'][:50] + '...' if len(latest['reason']) > 50 else latest['reason'],
                'Last_Update': latest['datetime']
            })
    
    if summary_data:
        df = pd.DataFrame(summary_data)
        return df.sort_values(['Signal', 'Strength'], ascending=[True, False])
    
    return pd.DataFrame()

def filter_stocks_by_signal(analysis_results: Dict[str, Dict], signal_type: str = 'BUY') -> List[Dict]:
    """
    Filter stocks by signal type.
    
    Args:
        analysis_results: Dictionary of analysis results
        signal_type: Signal type to filter ('BUY', 'SELL', 'HOLD')
        
    Returns:
        List of stocks with the specified signal
    """
    filtered_stocks = []
    
    for stock_symbol, result in analysis_results.items():
        if ('error' not in result and 
            result['latest_signal'] is not None and 
            result['latest_signal']['signal'] == signal_type):
            
            filtered_stocks.append({
                'stock': stock_symbol,
                'signal_data': result['latest_signal'],
                'statistics': result['statistics'],
                'full_data': result['data']
            })
    
    # Sort by signal strength
    filtered_stocks.sort(key=lambda x: abs(x['signal_data']['strength']), reverse=True)
    
    return filtered_stocks

def get_sector_performance(analysis_results: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Calculate sector-wise performance statistics.
    
    Args:
        analysis_results: Dictionary of analysis results
        
    Returns:
        Dictionary with sector performance data
    """
    from nifty50_stocks import get_sector_wise_stocks
    
    sectors = get_sector_wise_stocks()
    sector_performance = {}
    
    for sector, stocks in sectors.items():
        sector_data = {
            'total_stocks': 0,
            'buy_signals': 0,
            'sell_signals': 0,
            'hold_signals': 0,
            'avg_strength': 0,
            'stocks_with_signals': []
        }
        
        strengths = []
        
        for stock in stocks:
            if stock in analysis_results and 'error' not in analysis_results[stock]:
                result = analysis_results[stock]
                if result['latest_signal'] is not None:
                    sector_data['total_stocks'] += 1
                    signal = result['latest_signal']['signal']
                    strength = abs(result['latest_signal']['strength'])
                    
                    if signal == 'BUY':
                        sector_data['buy_signals'] += 1
                    elif signal == 'SELL':
                        sector_data['sell_signals'] += 1
                    else:
                        sector_data['hold_signals'] += 1
                    
                    if signal != 'HOLD':
                        strengths.append(strength)
                        sector_data['stocks_with_signals'].append({
                            'stock': stock,
                            'signal': signal,
                            'strength': strength
                        })
        
        if strengths:
            sector_data['avg_strength'] = np.mean(strengths)
        
        if sector_data['total_stocks'] > 0:
            sector_performance[sector] = sector_data
    
    return sector_performance

def calculate_portfolio_signals(analysis_results: Dict[str, Dict]) -> Dict[str, int]:
    """
    Calculate overall portfolio signal distribution.
    
    Args:
        analysis_results: Dictionary of analysis results
        
    Returns:
        Dictionary with signal counts
    """
    signals = {'BUY': 0, 'SELL': 0, 'HOLD': 0, 'ERROR': 0}
    
    for stock_symbol, result in analysis_results.items():
        if 'error' in result:
            signals['ERROR'] += 1
        elif result['latest_signal'] is not None:
            signal = result['latest_signal']['signal']
            signals[signal] += 1
        else:
            signals['ERROR'] += 1
    
    return signals
"""
Multi Stock Visualizations Module
Creates comprehensive visualizations for multi-stock trading signal analysis.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List

def create_portfolio_overview_chart(analysis_results: Dict[str, Dict]) -> go.Figure:
    """
    Create a portfolio overview chart showing signal distribution.
    
    Args:
        analysis_results: Dictionary of analysis results
        
    Returns:
        Plotly figure
    """
    # Count signals
    signal_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
    
    for result in analysis_results.values():
        if 'error' not in result and result['latest_signal'] is not None:
            signal = result['latest_signal']['signal']
            signal_counts[signal] += 1
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=list(signal_counts.keys()),
        values=list(signal_counts.values()),
        hole=0.4,
        marker=dict(
            colors=['#22c55e', '#ef4444', '#9ca3af'],
            line=dict(color='#1f2937', width=2)
        )
    )])
    
    fig.update_layout(
        title="Portfolio Signal Distribution",
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400
    )
    
    return fig

def create_sector_analysis_chart(sector_performance: Dict[str, Dict]) -> go.Figure:
    """
    Create sector analysis chart.
    
    Args:
        sector_performance: Dictionary with sector performance data
        
    Returns:
        Plotly figure
    """
    sectors = list(sector_performance.keys())
    buy_signals = [data['buy_signals'] for data in sector_performance.values()]
    sell_signals = [data['sell_signals'] for data in sector_performance.values()]
    total_stocks = [data['total_stocks'] for data in sector_performance.values()]
    
    fig = go.Figure()
    
    # Add buy signals
    fig.add_trace(go.Bar(
        name='Buy Signals',
        x=sectors,
        y=buy_signals,
        marker_color='#22c55e'
    ))
    
    # Add sell signals  
    fig.add_trace(go.Bar(
        name='Sell Signals',
        x=sectors,
        y=sell_signals,
        marker_color='#ef4444'
    ))
    
    fig.update_layout(
        title="Sector-wise Signal Distribution",
        xaxis_title="Sectors",
        yaxis_title="Number of Signals",
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    
    return fig

def create_signal_strength_heatmap(analysis_results: Dict[str, Dict]) -> go.Figure:
    """
    Create a heatmap showing signal strength across stocks.
    
    Args:
        analysis_results: Dictionary of analysis results
        
    Returns:
        Plotly figure
    """
    # Prepare data for heatmap
    stocks = []
    strengths = []
    signals = []
    
    for stock_symbol, result in analysis_results.items():
        if 'error' not in result and result['latest_signal'] is not None:
            stocks.append(stock_symbol)
            signal = result['latest_signal']['signal']
            strength = result['latest_signal']['strength']
            
            if signal == 'BUY':
                strengths.append(strength)
            elif signal == 'SELL':
                strengths.append(-abs(strength))  # Negative for sell
            else:
                strengths.append(0)
            
            signals.append(signal)
    
    # Sort by strength
    sorted_data = sorted(zip(stocks, strengths, signals), key=lambda x: x[1], reverse=True)
    stocks, strengths, signals = zip(*sorted_data) if sorted_data else ([], [], [])
    
    # Create color scale based on signal type
    colors = []
    for signal, strength in zip(signals, strengths):
        if signal == 'BUY':
            colors.append(f'rgba(34, 197, 94, {min(abs(strength)/3, 1)})')  # Green
        elif signal == 'SELL':
            colors.append(f'rgba(239, 68, 68, {min(abs(strength)/3, 1)})')  # Red
        else:
            colors.append('rgba(156, 163, 175, 0.3)')  # Gray
    
    fig = go.Figure(data=go.Bar(
        x=stocks,
        y=strengths,
        marker_color=colors,
        text=[f"{s}<br>{sig}" for s, sig in zip(strengths, signals)],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Signal Strength Across Stocks",
        xaxis_title="Stocks",
        yaxis_title="Signal Strength",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=600,
        xaxis=dict(tickangle=-45)
    )
    
    return fig

def create_top_signals_table(analysis_results: Dict[str, Dict], signal_type: str = 'BUY', top_n: int = 10) -> pd.DataFrame:
    """
    Create a table of top signals.
    
    Args:
        analysis_results: Dictionary of analysis results
        signal_type: Type of signal to show
        top_n: Number of top signals to show
        
    Returns:
        DataFrame with top signals
    """
    signal_data = []
    
    for stock_symbol, result in analysis_results.items():
        if ('error' not in result and 
            result['latest_signal'] is not None and 
            result['latest_signal']['signal'] == signal_type):
            
            latest = result['latest_signal']
            signal_data.append({
                'Stock': stock_symbol,
                'Signal': latest['signal'],
                'Strength': abs(latest['strength']),
                'Price': f"₹{latest['close_price']:.2f}",
                'MACD': f"{latest['macd']:.4f}",
                'MFI': f"{latest['mfi']:.1f}",
                'Doji': '✓' if latest['is_doji'] else '✗',
                'Reason': latest['reason']
            })
    
    if signal_data:
        df = pd.DataFrame(signal_data)
        return df.sort_values('Strength', ascending=False).head(top_n)
    
    return pd.DataFrame()

def create_mfi_macd_scatter(analysis_results: Dict[str, Dict]) -> go.Figure:
    """
    Create scatter plot of MFI vs MACD with signal coloring.
    
    Args:
        analysis_results: Dictionary of analysis results
        
    Returns:
        Plotly figure
    """
    mfi_values = []
    macd_values = []
    signals = []
    stocks = []
    
    for stock_symbol, result in analysis_results.items():
        if 'error' not in result and result['latest_signal'] is not None:
            latest = result['latest_signal']
            mfi_values.append(latest['mfi'])
            macd_values.append(latest['macd'])
            signals.append(latest['signal'])
            stocks.append(stock_symbol)
    
    # Create color mapping
    color_map = {'BUY': '#22c55e', 'SELL': '#ef4444', 'HOLD': '#9ca3af'}
    colors = [color_map[signal] for signal in signals]
    
    fig = go.Figure()
    
    # Add scatter plot
    fig.add_trace(go.Scatter(
        x=mfi_values,
        y=macd_values,
        mode='markers',
        marker=dict(
            color=colors,
            size=10,
            line=dict(width=1, color='white')
        ),
        text=stocks,
        textposition='top center',
        name='Stocks'
    ))
    
    # Add reference lines
    fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
    fig.add_vline(x=30, line_dash="dash", line_color="orange", opacity=0.5, annotation_text="Oversold")
    fig.add_vline(x=70, line_dash="dash", line_color="orange", opacity=0.5, annotation_text="Overbought")
    
    fig.update_layout(
        title="MFI vs MACD Signal Analysis",
        xaxis_title="MFI",
        yaxis_title="MACD",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    
    return fig

def create_individual_stock_chart(stock_data: pd.DataFrame, stock_name: str) -> go.Figure:
    """
    Create detailed chart for individual stock.
    
    Args:
        stock_data: DataFrame with stock data and indicators
        stock_name: Name of the stock
        
    Returns:
        Plotly figure
    """
    # Create subplots
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxis=True,
        vertical_spacing=0.05,
        subplot_titles=[
            f'{stock_name} - Heikin Ashi Candles',
            'MACD',
            'MFI',
            'Signals'
        ],
        row_heights=[0.4, 0.2, 0.2, 0.2]
    )
    
    # Heikin Ashi candlestick chart
    fig.add_trace(go.Candlestick(
        x=stock_data['Datetime'],
        open=stock_data['HA_Open'],
        high=stock_data['HA_High'],
        low=stock_data['HA_Low'],
        close=stock_data['HA_Close'],
        name='Heikin Ashi',
        increasing_line_color='#22c55e',
        decreasing_line_color='#ef4444'
    ), row=1, col=1)
    
    # Mark Doji patterns
    doji_points = stock_data[stock_data['Is_Doji']]
    if not doji_points.empty:
        fig.add_trace(go.Scatter(
            x=doji_points['Datetime'],
            y=doji_points['HA_High'] * 1.01,
            mode='markers',
            marker=dict(symbol='star', size=8, color='yellow'),
            name='Doji',
            showlegend=True
        ), row=1, col=1)
    
    # MACD
    if 'MACD' in stock_data.columns:
        fig.add_trace(go.Scatter(
            x=stock_data['Datetime'],
            y=stock_data['MACD'],
            name='MACD',
            line=dict(color='blue')
        ), row=2, col=1)
        
        fig.add_trace(go.Scatter(
            x=stock_data['Datetime'],
            y=stock_data['MACD_Signal'],
            name='MACD Signal',
            line=dict(color='red')
        ), row=2, col=1)
    
    # MFI
    if 'MFI' in stock_data.columns:
        fig.add_trace(go.Scatter(
            x=stock_data['Datetime'],
            y=stock_data['MFI'],
            name='MFI',
            line=dict(color='purple')
        ), row=3, col=1)
        
        # Add MFI reference lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=3, col=1)
    
    # Trading signals
    buy_signals = stock_data[stock_data['Signal'] == 'BUY']
    sell_signals = stock_data[stock_data['Signal'] == 'SELL']
    
    if not buy_signals.empty:
        fig.add_trace(go.Scatter(
            x=buy_signals['Datetime'],
            y=[1] * len(buy_signals),
            mode='markers',
            marker=dict(symbol='triangle-up', size=10, color='green'),
            name='Buy Signal'
        ), row=4, col=1)
    
    if not sell_signals.empty:
        fig.add_trace(go.Scatter(
            x=sell_signals['Datetime'],
            y=[-1] * len(sell_signals),
            mode='markers',
            marker=dict(symbol='triangle-down', size=10, color='red'),
            name='Sell Signal'
        ), row=4, col=1)
    
    # Update layout
    fig.update_layout(
        height=800,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        xaxis_rangeslider_visible=False
    )
    
    return fig

def create_correlation_matrix(analysis_results: Dict[str, Dict]) -> go.Figure:
    """
    Create correlation matrix between different indicators.
    
    Args:
        analysis_results: Dictionary of analysis results
        
    Returns:
        Plotly figure
    """
    # Collect indicator data
    indicator_data = []
    
    for stock_symbol, result in analysis_results.items():
        if 'error' not in result and not result['data'].empty:
            data = result['data']
            if len(data) > 0:
                latest = data.iloc[-1]
                indicator_data.append({
                    'Stock': stock_symbol,
                    'MACD': latest.get('MACD', 0),
                    'MFI': latest.get('MFI', 50),
                    'Close': latest['Close'],
                    'Volume': latest['Volume'],
                    'Signal_Strength': abs(latest.get('Signal_Strength', 0))
                })
    
    if indicator_data:
        df = pd.DataFrame(indicator_data)
        
        # Calculate correlation matrix
        numeric_cols = ['MACD', 'MFI', 'Close', 'Volume', 'Signal_Strength']
        corr_matrix = df[numeric_cols].corr()
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate="%{text}",
            textfont={"size": 12},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Indicator Correlation Matrix",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=500
        )
        
        return fig
    
    return go.Figure()
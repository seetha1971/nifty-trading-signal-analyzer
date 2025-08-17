"""
Visualizations Module
Contains functions for creating trading charts and visualizations.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
from typing import Optional, Dict, Any


def create_heikinashi_chart(df: pd.DataFrame, show_signals: bool = True) -> go.Figure:
    """
    Create a Heikin-Ashi candlestick chart with trading signals.
    
    Args:
        df: DataFrame with Heikin-Ashi data and signals
        show_signals: Whether to show trading signals on the chart
        
    Returns:
        Plotly figure object
    """
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=('Heikin-Ashi Candlesticks', 'MACD', 'MFI', 'Volume'),
        row_heights=[0.5, 0.2, 0.15, 0.15]
    )
    
    # Heikin-Ashi Candlesticks
    fig.add_trace(
        go.Candlestick(
            x=df['Datetime'],
            open=df['HA_Open'],
            high=df['HA_High'],
            low=df['HA_Low'],
            close=df['HA_Close'],
            name='Heikin-Ashi',
            increasing_line_color='#00ff88',
            decreasing_line_color='#ff4444',
            increasing_fillcolor='#00ff88',
            decreasing_fillcolor='#ff4444'
        ),
        row=1, col=1
    )
    
    # Add Doji markers
    doji_data = df[df['Is_Doji']]
    if not doji_data.empty:
        fig.add_trace(
            go.Scatter(
                x=doji_data['Datetime'],
                y=doji_data['HA_High'],
                mode='markers',
                marker=dict(
                    symbol='diamond',
                    size=10,
                    color='yellow',
                    line=dict(color='orange', width=1)
                ),
                name='Doji',
                hovertext=['Doji Candle'] * len(doji_data)
            ),
            row=1, col=1
        )
    
    # Add trading signals
    if show_signals:
        # Buy signals
        buy_signals = df[df['Signal'] == 'BUY']
        if not buy_signals.empty:
            colors = {1: 'lightgreen', 2: 'green', 3: 'darkgreen'}
            sizes = {1: 8, 2: 10, 3: 12}
            
            for strength in [1, 2, 3]:
                strength_signals = buy_signals[buy_signals['Signal_Strength'] == strength]
                if not strength_signals.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=strength_signals['Datetime'],
                            y=strength_signals['HA_Low'],
                            mode='markers',
                            marker=dict(
                                symbol='triangle-up',
                                size=sizes[strength],
                                color=colors[strength],
                                line=dict(color='white', width=1)
                            ),
                            name=f'BUY (Strength {strength})',
                            hovertext=[f"BUY: {reason}" for reason in strength_signals['Signal_Reason']]
                        ),
                        row=1, col=1
                    )
        
        # Sell signals
        sell_signals = df[df['Signal'] == 'SELL']
        if not sell_signals.empty:
            colors = {-1: 'lightcoral', -2: 'red', -3: 'darkred'}
            sizes = {-1: 8, -2: 10, -3: 12}
            
            for strength in [-1, -2, -3]:
                strength_signals = sell_signals[sell_signals['Signal_Strength'] == strength]
                if not strength_signals.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=strength_signals['Datetime'],
                            y=strength_signals['HA_High'],
                            mode='markers',
                            marker=dict(
                                symbol='triangle-down',
                                size=sizes[strength],
                                color=colors[strength],
                                line=dict(color='white', width=1)
                            ),
                            name=f'SELL (Strength {abs(strength)})',
                            hovertext=[f"SELL: {reason}" for reason in strength_signals['Signal_Reason']]
                        ),
                        row=1, col=1
                    )
    
    # MACD
    fig.add_trace(
        go.Scatter(
            x=df['Datetime'],
            y=df['MACD'],
            mode='lines',
            name='MACD',
            line=dict(color='blue', width=2)
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['Datetime'],
            y=df['MACD_Signal'],
            mode='lines',
            name='Signal',
            line=dict(color='red', width=2)
        ),
        row=2, col=1
    )
    
    # MACD Histogram
    colors = ['green' if val >= 0 else 'red' for val in df['MACD_Histogram']]
    fig.add_trace(
        go.Bar(
            x=df['Datetime'],
            y=df['MACD_Histogram'],
            name='MACD Histogram',
            marker_color=colors,
            opacity=0.6
        ),
        row=2, col=1
    )
    
    # MFI
    fig.add_trace(
        go.Scatter(
            x=df['Datetime'],
            y=df['MFI'],
            mode='lines',
            name='MFI',
            line=dict(color='purple', width=2)
        ),
        row=3, col=1
    )
    
    # Add MFI overbought/oversold lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=3, col=1)
    
    # Volume
    volume_colors = ['green' if close >= open_price else 'red' 
                    for close, open_price in zip(df['Close'], df['Open'])]
    
    fig.add_trace(
        go.Bar(
            x=df['Datetime'],
            y=df['Volume'],
            name='Volume',
            marker_color=volume_colors,
            opacity=0.6
        ),
        row=4, col=1
    )
    
    # Update layout
    fig.update_layout(
        title='NIFTY Trading Signal Analysis',
        xaxis_title='Time',
        template='plotly_dark',
        height=800,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update y-axis titles
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)
    fig.update_yaxes(title_text="MFI", row=3, col=1)
    fig.update_yaxes(title_text="Volume", row=4, col=1)
    
    # Remove x-axis labels for all but bottom subplot
    fig.update_xaxes(showticklabels=False, row=1, col=1)
    fig.update_xaxes(showticklabels=False, row=2, col=1)
    fig.update_xaxes(showticklabels=False, row=3, col=1)
    
    return fig


def create_signals_summary_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a summary chart showing signal distribution.
    
    Args:
        df: DataFrame with signals
        
    Returns:
        Plotly figure object
    """
    # Count signals by type
    signal_counts = df['Signal'].value_counts()
    
    # Create pie chart
    fig = go.Figure(data=[
        go.Pie(
            labels=signal_counts.index,
            values=signal_counts.values,
            hole=0.3,
            marker_colors=['green', 'red', 'gray']
        )
    ])
    
    fig.update_layout(
        title='Trading Signals Distribution',
        template='plotly_dark',
        height=400
    )
    
    return fig


def create_strength_analysis_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a chart showing signal strength distribution.
    
    Args:
        df: DataFrame with signals and strengths
        
    Returns:
        Plotly figure object
    """
    # Filter out HOLD signals
    signal_df = df[df['Signal'] != 'HOLD']
    
    if signal_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No trading signals found in the data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="white")
        )
        fig.update_layout(
            title='Signal Strength Analysis',
            template='plotly_dark',
            height=400
        )
        return fig
    
    # Count signals by strength
    strength_counts = signal_df['Signal_Strength'].value_counts().sort_index()
    
    # Create bar chart
    colors = ['darkred' if x < 0 else 'darkgreen' for x in strength_counts.index]
    
    fig = go.Figure(data=[
        go.Bar(
            x=strength_counts.index,
            y=strength_counts.values,
            marker_color=colors,
            text=strength_counts.values,
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title='Signal Strength Distribution',
        xaxis_title='Signal Strength',
        yaxis_title='Count',
        template='plotly_dark',
        height=400
    )
    
    return fig


def create_performance_metrics_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a performance metrics table.
    
    Args:
        df: DataFrame with signals and price data
        
    Returns:
        DataFrame with performance metrics
    """
    metrics = {}
    
    # Basic statistics
    metrics['Total Signals'] = len(df[df['Signal'] != 'HOLD'])
    metrics['Buy Signals'] = len(df[df['Signal'] == 'BUY'])
    metrics['Sell Signals'] = len(df[df['Signal'] == 'SELL'])
    metrics['Hold Periods'] = len(df[df['Signal'] == 'HOLD'])
    
    # Signal strength breakdown
    signal_df = df[df['Signal'] != 'HOLD']
    if not signal_df.empty:
        metrics['Average Signal Strength'] = signal_df['Signal_Strength'].abs().mean()
        metrics['Strong Signals (|3|)'] = len(signal_df[signal_df['Signal_Strength'].abs() == 3])
        metrics['Medium Signals (|2|)'] = len(signal_df[signal_df['Signal_Strength'].abs() == 2])
        metrics['Weak Signals (|1|)'] = len(signal_df[signal_df['Signal_Strength'].abs() == 1])
    
    # Doji statistics
    metrics['Total Doji Candles'] = len(df[df['Is_Doji']])
    metrics['Doji with Signals'] = len(df[df['Is_Doji'] & (df['Signal'] != 'HOLD')])
    
    # Price statistics
    if not df.empty:
        metrics['Current Price'] = df['Close'].iloc[-1]
        metrics['Highest Price'] = df['High'].max()
        metrics['Lowest Price'] = df['Low'].min()
        metrics['Price Range'] = metrics['Highest Price'] - metrics['Lowest Price']
        metrics['Average Volume'] = df['Volume'].mean()
    
    # Convert to DataFrame for display
    metrics_df = pd.DataFrame.from_dict(metrics, orient='index', columns=['Value'])
    metrics_df.index.name = 'Metric'
    
    return metrics_df


def display_latest_signals_table(df: pd.DataFrame, num_signals: int = 10) -> pd.DataFrame:
    """
    Create a table of the latest trading signals.
    
    Args:
        df: DataFrame with signals
        num_signals: Number of latest signals to show
        
    Returns:
        DataFrame with latest signals
    """
    # Get signals only (exclude HOLD)
    signals_df = df[df['Signal'] != 'HOLD'].copy()
    
    if signals_df.empty:
        return pd.DataFrame(columns=['Datetime', 'Signal', 'Strength', 'Reason', 'Price'])
    
    # Get the latest signals
    latest_signals = signals_df.tail(num_signals)
    
    # Create display table
    display_df = pd.DataFrame({
        'Datetime': latest_signals['Datetime'].dt.strftime('%Y-%m-%d %H:%M'),
        'Signal': latest_signals['Signal'],
        'Strength': latest_signals['Signal_Strength'],
        'Reason': latest_signals['Signal_Reason'],
        'Price': latest_signals['Close'].round(2)
    })
    
    return display_df.sort_values('Datetime', ascending=False)


def create_indicator_correlation_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a correlation heatmap of indicators.
    
    Args:
        df: DataFrame with calculated indicators
        
    Returns:
        Plotly figure object
    """
    # Select numeric columns for correlation
    numeric_cols = ['Close', 'MFI', 'MACD', 'MACD_Signal', 'MACD_Histogram']
    
    # Calculate correlation matrix
    corr_matrix = df[numeric_cols].corr()
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(3),
        texttemplate="%{text}",
        textfont={"size": 10},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title='Indicator Correlation Matrix',
        template='plotly_dark',
        height=500,
        width=600
    )
    
    return fig
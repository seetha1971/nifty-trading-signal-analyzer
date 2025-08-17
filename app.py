"""
NIFTY Trading Signal Analyzer
A comprehensive trading application that analyzes NIFTY signals using Heikin-Ashi Doji candles,
Money Flow Index (MFI), and MACD crossovers.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Import our custom modules
from data_fetcher import (
    fetch_nifty_data, 
    get_available_periods, 
    get_available_intervals,
    validate_period_interval_combination,
    preprocess_data,
    get_latest_price_info
)
from trading_indicators import calculate_all_indicators
from visualizations import (
    create_heikinashi_chart,
    create_signals_summary_chart,
    create_strength_analysis_chart,
    create_performance_metrics_table,
    display_latest_signals_table,
    create_indicator_correlation_chart
)

# Page configuration
st.set_page_config(
    page_title="NIFTY Trading Signal Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-container {
        background-color: #1f2937;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #374151;
    }
    .signal-buy {
        background-color: rgba(34, 197, 94, 0.1);
        border-left: 4px solid #22c55e;
        padding: 0.5rem;
        margin: 0.25rem 0;
    }
    .signal-sell {
        background-color: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
        padding: 0.5rem;
        margin: 0.25rem 0;
    }
    .signal-hold {
        background-color: rgba(156, 163, 175, 0.1);
        border-left: 4px solid #9ca3af;
        padding: 0.5rem;
        margin: 0.25rem 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Title and description
    st.title("📈 NIFTY Trading Signal Analyzer")
    st.markdown("""
    Advanced trading signal analysis using **Heikin-Ashi Doji candles**, **Money Flow Index (MFI)**, 
    and **MACD crossovers** on 15-minute timeframe data from Yahoo Finance.
    """)
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Data fetching parameters
    st.sidebar.subheader("Data Parameters")
    
    periods = get_available_periods()
    intervals = get_available_intervals()
    
    selected_period = st.sidebar.selectbox(
        "Select Time Period:",
        options=list(periods.keys()),
        index=list(periods.keys()).index("1 Month")
    )
    
    selected_interval = st.sidebar.selectbox(
        "Select Time Interval:",
        options=list(intervals.keys()),
        index=list(intervals.keys()).index("15 Minutes")
    )
    
    period_code = periods[selected_period]
    interval_code = intervals[selected_interval]
    
    # Validate period-interval combination
    if not validate_period_interval_combination(period_code, interval_code):
        st.sidebar.error(f"⚠️ {selected_period} period is not compatible with {selected_interval} interval")
        st.sidebar.info("Please select a different combination")
        return
    
    # Indicator parameters
    st.sidebar.subheader("Indicator Parameters")
    
    doji_threshold = st.sidebar.slider(
        "Doji Threshold:", 
        min_value=0.05, 
        max_value=0.3, 
        value=0.1, 
        step=0.05,
        help="Body size threshold for Doji detection (smaller = stricter)"
    )
    
    mfi_oversold = st.sidebar.slider(
        "MFI Oversold Level:", 
        min_value=10, 
        max_value=40, 
        value=30,
        help="MFI level considered oversold (buy signal)"
    )
    
    mfi_overbought = st.sidebar.slider(
        "MFI Overbought Level:", 
        min_value=60, 
        max_value=90, 
        value=70,
        help="MFI level considered overbought (sell signal)"
    )
    
    # Fetch data button
    fetch_data = st.sidebar.button("🔄 Fetch Latest Data", type="primary")
    
    # Auto-refresh option
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (5 min)", value=False)
    
    if auto_refresh:
        st.rerun()
    
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    
    # Fetch data
    if fetch_data or st.session_state.data is None:
        with st.spinner("Fetching NIFTY data..."):
            raw_data = fetch_nifty_data(period=period_code, interval=interval_code)
            
            if raw_data is not None:
                st.session_state.data = raw_data
                st.sidebar.success(f"✅ Fetched {len(raw_data)} data points")
            else:
                st.sidebar.error("❌ Failed to fetch data")
                return
    
    # Process data
    if st.session_state.data is not None:
        with st.spinner("Processing indicators..."):
            # Preprocess data
            preprocessed_data = preprocess_data(st.session_state.data)
            
            # Calculate all indicators
            processed_data = calculate_all_indicators(preprocessed_data)
            st.session_state.processed_data = processed_data
    
    # Display results
    if st.session_state.processed_data is not None:
        df = st.session_state.processed_data
        
        # Get latest price info
        price_info = get_latest_price_info(st.session_state.data)
        
        # Main dashboard
        display_dashboard(df, price_info)
        
    else:
        st.info("👆 Please fetch data using the button in the sidebar to begin analysis.")


def display_dashboard(df: pd.DataFrame, price_info: dict):
    """Display the main dashboard with all charts and metrics."""
    
    # Latest price information
    if price_info:
        st.subheader("💰 Latest Market Information")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Current Price", 
                f"₹{price_info['close']:.2f}",
                delta=f"{price_info['change']:+.2f} ({price_info['change_percent']:+.2f}%)"
            )
        
        with col2:
            st.metric("Open", f"₹{price_info['open']:.2f}")
        
        with col3:
            st.metric("High", f"₹{price_info['high']:.2f}")
        
        with col4:
            st.metric("Low", f"₹{price_info['low']:.2f}")
        
        with col5:
            st.metric("Volume", f"{price_info['volume']:,.0f}")
        
        st.markdown("---")
    
    # Current signal status
    st.subheader("🚨 Current Signal Status")
    
    if not df.empty:
        latest_signal = df.iloc[-1]
        signal_type = latest_signal['Signal']
        signal_strength = latest_signal['Signal_Strength']
        signal_reason = latest_signal['Signal_Reason']
        
        if signal_type == 'BUY':
            st.markdown(f"""
            <div class="signal-buy">
                <h3>🟢 BUY SIGNAL</h3>
                <p><strong>Strength:</strong> {signal_strength}/3</p>
                <p><strong>Reason:</strong> {signal_reason}</p>
            </div>
            """, unsafe_allow_html=True)
        elif signal_type == 'SELL':
            st.markdown(f"""
            <div class="signal-sell">
                <h3>🔴 SELL SIGNAL</h3>
                <p><strong>Strength:</strong> {abs(signal_strength)}/3</p>
                <p><strong>Reason:</strong> {signal_reason}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="signal-hold">
                <h3>⚫ HOLD</h3>
                <p>No trading signal detected</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main chart
    st.subheader("📊 Heikin-Ashi Trading Chart")
    
    chart = create_heikinashi_chart(df, show_signals=True)
    st.plotly_chart(chart, use_container_width=True)
    
    # Analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Signals Analysis", "📊 Performance Metrics", "🔗 Correlations", "📋 Signal History"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Signal Distribution")
            signals_chart = create_signals_summary_chart(df)
            st.plotly_chart(signals_chart, use_container_width=True)
        
        with col2:
            st.subheader("Signal Strength Analysis")
            strength_chart = create_strength_analysis_chart(df)
            st.plotly_chart(strength_chart, use_container_width=True)
    
    with tab2:
        st.subheader("Performance Metrics")
        metrics_df = create_performance_metrics_table(df)
        st.dataframe(metrics_df, use_container_width=True)
        
        # Additional metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            doji_count = len(df[df['Is_Doji']])
            total_candles = len(df)
            doji_percentage = (doji_count / total_candles) * 100
            st.metric("Doji Percentage", f"{doji_percentage:.1f}%")
        
        with col2:
            signal_count = len(df[df['Signal'] != 'HOLD'])
            signal_percentage = (signal_count / total_candles) * 100
            st.metric("Signal Activity", f"{signal_percentage:.1f}%")
        
        with col3:
            if 'MFI' in df.columns:
                current_mfi = df['MFI'].iloc[-1]
                st.metric("Current MFI", f"{current_mfi:.1f}")
    
    with tab3:
        st.subheader("Indicator Correlations")
        corr_chart = create_indicator_correlation_chart(df)
        st.plotly_chart(corr_chart, use_container_width=True)
        
        # Key insights
        st.subheader("Key Insights")
        
        # Calculate some insights
        total_signals = len(df[df['Signal'] != 'HOLD'])
        buy_signals = len(df[df['Signal'] == 'BUY'])
        sell_signals = len(df[df['Signal'] == 'SELL'])
        
        if total_signals > 0:
            buy_percentage = (buy_signals / total_signals) * 100
            sell_percentage = (sell_signals / total_signals) * 100
            
            st.write(f"• **Signal Bias:** {buy_percentage:.1f}% BUY vs {sell_percentage:.1f}% SELL signals")
        
        # Doji with signals
        doji_with_signals = len(df[df['Is_Doji'] & (df['Signal'] != 'HOLD')])
        total_doji = len(df[df['Is_Doji']])
        
        if total_doji > 0:
            doji_signal_rate = (doji_with_signals / total_doji) * 100
            st.write(f"• **Doji Effectiveness:** {doji_signal_rate:.1f}% of Doji candles generated signals")
    
    with tab4:
        st.subheader("Latest Trading Signals")
        signals_table = display_latest_signals_table(df, num_signals=20)
        
        if not signals_table.empty:
            st.dataframe(signals_table, use_container_width=True)
        else:
            st.info("No trading signals found in the current dataset.")
        
        # Export functionality
        if not signals_table.empty:
            csv = signals_table.to_csv(index=False)
            st.download_button(
                label="📥 Download Signal History (CSV)",
                data=csv,
                file_name=f"nifty_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )


if __name__ == "__main__":
    main()
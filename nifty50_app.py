"""
Nifty 50 FNO Trading Signal Analyzer
Comprehensive analysis of top 50 Nifty 50 FNO stocks using Heikin Ashi Doji, MACD, and MFI.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# Import custom modules
from nifty50_stocks import get_nifty50_stocks, get_sector_wise_stocks, get_top_fno_stocks
from multi_stock_fetcher import fetch_nifty50_data, get_stock_summary, validate_stock_data
from multi_stock_analyzer import (
    analyze_multiple_stocks, 
    create_signals_summary, 
    filter_stocks_by_signal,
    get_sector_performance,
    calculate_portfolio_signals
)
from multi_stock_visualizations import (
    create_portfolio_overview_chart,
    create_sector_analysis_chart,
    create_signal_strength_heatmap,
    create_top_signals_table,
    create_mfi_macd_scatter,
    create_individual_stock_chart,
    create_correlation_matrix
)

# Page configuration
st.set_page_config(
    page_title="Nifty 50 FNO Trading Signal Analyzer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f2937 0%, #374151 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .metric-card {
        background-color: #1f2937;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #374151;
        text-align: center;
    }
    .signal-buy {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(34, 197, 94, 0.2));
        border-left: 4px solid #22c55e;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .signal-sell {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.2));
        border-left: 4px solid #ef4444;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .signal-neutral {
        background: linear-gradient(135deg, rgba(156, 163, 175, 0.1), rgba(156, 163, 175, 0.2));
        border-left: 4px solid #9ca3af;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Nifty 50 FNO Trading Signal Analyzer</h1>
        <p>Comprehensive analysis of top 50 Nifty 50 FNO stocks using <strong>Heikin Ashi Doji</strong>, <strong>MACD</strong>, and <strong>MFI</strong> indicators</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Analysis Configuration")
    
    # Stock selection
    st.sidebar.subheader("Stock Selection")
    num_stocks = st.sidebar.slider(
        "Number of stocks to analyze:",
        min_value=10,
        max_value=50,
        value=30,
        step=5,
        help="Select number of top Nifty 50 stocks to analyze"
    )
    
    # Data parameters
    st.sidebar.subheader("Data Parameters")
    period = st.sidebar.selectbox(
        "Time Period:",
        options=["1mo", "3mo", "6mo"],
        index=0,
        help="Data collection period"
    )
    
    interval = st.sidebar.selectbox(
        "Time Interval:",
        options=["15m", "1h", "1d"],
        index=0,
        help="Data granularity"
    )
    
    # Indicator parameters
    st.sidebar.subheader("Indicator Parameters")
    
    doji_threshold = st.sidebar.slider(
        "Doji Threshold:",
        min_value=0.05,
        max_value=0.3,
        value=0.1,
        step=0.05,
        help="Body size threshold for Doji detection"
    )
    
    mfi_oversold = st.sidebar.slider(
        "MFI Oversold Level:",
        min_value=10,
        max_value=40,
        value=30,
        help="MFI level considered oversold"
    )
    
    mfi_overbought = st.sidebar.slider(
        "MFI Overbought Level:",
        min_value=60,
        max_value=90,
        value=70,
        help="MFI level considered overbought"
    )
    
    # Analysis controls
    st.sidebar.subheader("Analysis Controls")
    analyze_button = st.sidebar.button("🔍 Start Analysis", type="primary")
    
    auto_refresh = st.sidebar.checkbox(
        "🔄 Auto-refresh (10 min)",
        value=False,
        help="Automatically refresh analysis every 10 minutes"
    )
    
    if auto_refresh:
        time.sleep(600)  # 10 minutes
        st.rerun()
    
    # Initialize session state
    if 'stock_data' not in st.session_state:
        st.session_state.stock_data = {}
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}
    if 'last_analysis_time' not in st.session_state:
        st.session_state.last_analysis_time = None
    
    # Run analysis
    if analyze_button or (not st.session_state.stock_data):
        run_analysis(num_stocks, period, interval, doji_threshold, mfi_oversold, mfi_overbought)
    
    # Display results
    if st.session_state.analysis_results:
        display_analysis_results()
    else:
        st.info("👆 Click 'Start Analysis' to begin analyzing Nifty 50 FNO stocks")

def run_analysis(num_stocks, period, interval, doji_threshold, mfi_oversold, mfi_overbought):
    """Run the complete stock analysis pipeline."""
    
    st.header("📊 Analysis In Progress")
    
    with st.spinner("Initializing analysis..."):
        progress_container = st.container()
        
        with progress_container:
            # Step 1: Fetch stock data
            st.subheader("📈 Fetching Stock Data")
            stock_data = fetch_nifty50_data(period=period, interval=interval, top_n=num_stocks)
            
            if not stock_data:
                st.error("❌ Failed to fetch stock data. Please try again.")
                return
            
            # Validate data
            validated_data = validate_stock_data(stock_data)
            st.success(f"✅ Successfully fetched data for {len(validated_data)} stocks")
            
            # Step 2: Analyze stocks
            st.subheader("🔍 Analyzing Trading Signals")
            analysis_results = analyze_multiple_stocks(
                validated_data,
                doji_threshold=doji_threshold,
                mfi_oversold=mfi_oversold,
                mfi_overbought=mfi_overbought
            )
            
            # Store results in session state
            st.session_state.stock_data = validated_data
            st.session_state.analysis_results = analysis_results
            st.session_state.last_analysis_time = datetime.now()
            
            st.success(f"✅ Analysis complete for {len(analysis_results)} stocks")

def display_analysis_results():
    """Display comprehensive analysis results."""
    
    analysis_results = st.session_state.analysis_results
    stock_data = st.session_state.stock_data
    
    # Analysis timestamp
    if st.session_state.last_analysis_time:
        st.caption(f"Last analyzed: {st.session_state.last_analysis_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Portfolio overview
    st.header("📊 Portfolio Overview")
    
    # Calculate portfolio signals
    portfolio_signals = calculate_portfolio_signals(analysis_results)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #22c55e;">BUY SIGNALS</h3>
            <h1>{portfolio_signals['BUY']}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #ef4444;">SELL SIGNALS</h3>
            <h1>{portfolio_signals['SELL']}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #9ca3af;">HOLD</h3>
            <h1>{portfolio_signals['HOLD']}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_analyzed = sum(portfolio_signals.values())
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #3b82f6;">TOTAL ANALYZED</h3>
            <h1>{total_analyzed}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    # Portfolio charts
    col1, col2 = st.columns(2)
    
    with col1:
        portfolio_chart = create_portfolio_overview_chart(analysis_results)
        st.plotly_chart(portfolio_chart, use_container_width=True)
    
    with col2:
        strength_chart = create_signal_strength_heatmap(analysis_results)
        st.plotly_chart(strength_chart, use_container_width=True)
    
    # Analysis tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 Top Signals",
        "🏭 Sector Analysis", 
        "📈 MFI vs MACD",
        "🔗 Correlations",
        "📋 All Signals",
        "📊 Individual Stocks"
    ])
    
    with tab1:
        display_top_signals(analysis_results)
    
    with tab2:
        display_sector_analysis(analysis_results)
    
    with tab3:
        display_mfi_macd_analysis(analysis_results)
    
    with tab4:
        display_correlation_analysis(analysis_results)
    
    with tab5:
        display_all_signals(analysis_results)
    
    with tab6:
        display_individual_stock_analysis(analysis_results, stock_data)

def display_top_signals(analysis_results):
    """Display top trading signals."""
    
    st.subheader("🎯 Top Trading Signals")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🟢 Top BUY Signals")
        buy_table = create_top_signals_table(analysis_results, 'BUY', 10)
        if not buy_table.empty:
            st.dataframe(buy_table, use_container_width=True, hide_index=True)
        else:
            st.info("No BUY signals found")
    
    with col2:
        st.markdown("### 🔴 Top SELL Signals")
        sell_table = create_top_signals_table(analysis_results, 'SELL', 10)
        if not sell_table.empty:
            st.dataframe(sell_table, use_container_width=True, hide_index=True)
        else:
            st.info("No SELL signals found")
    
    # Export functionality
    st.subheader("📥 Export Signals")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not buy_table.empty:
            csv_buy = buy_table.to_csv(index=False)
            st.download_button(
                label="Download BUY Signals",
                data=csv_buy,
                file_name=f"buy_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if not sell_table.empty:
            csv_sell = sell_table.to_csv(index=False)
            st.download_button(
                label="Download SELL Signals", 
                data=csv_sell,
                file_name=f"sell_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col3:
        all_signals = create_signals_summary(analysis_results)
        if not all_signals.empty:
            csv_all = all_signals.to_csv(index=False)
            st.download_button(
                label="Download All Signals",
                data=csv_all,
                file_name=f"all_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

def display_sector_analysis(analysis_results):
    """Display sector-wise analysis."""
    
    st.subheader("🏭 Sector Analysis")
    
    sector_performance = get_sector_performance(analysis_results)
    
    if sector_performance:
        # Sector performance chart
        sector_chart = create_sector_analysis_chart(sector_performance)
        st.plotly_chart(sector_chart, use_container_width=True)
        
        # Sector details
        st.subheader("📊 Sector Details")
        
        sector_data = []
        for sector, data in sector_performance.items():
            sector_data.append({
                'Sector': sector,
                'Total Stocks': data['total_stocks'],
                'BUY Signals': data['buy_signals'],
                'SELL Signals': data['sell_signals'],
                'HOLD': data['hold_signals'],
                'Avg Strength': round(data['avg_strength'], 2),
                'Signal Rate %': round((data['buy_signals'] + data['sell_signals']) / data['total_stocks'] * 100, 1)
            })
        
        sector_df = pd.DataFrame(sector_data)
        st.dataframe(sector_df, use_container_width=True, hide_index=True)
    else:
        st.info("No sector data available")

def display_mfi_macd_analysis(analysis_results):
    """Display MFI vs MACD analysis."""
    
    st.subheader("📈 MFI vs MACD Analysis")
    
    scatter_chart = create_mfi_macd_scatter(analysis_results)
    st.plotly_chart(scatter_chart, use_container_width=True)
    
    # Analysis insights
    st.subheader("💡 Key Insights")
    
    # Calculate insights
    mfi_oversold_count = sum(1 for result in analysis_results.values() 
                           if 'error' not in result and result['latest_signal'] is not None 
                           and result['latest_signal']['mfi'] < 30)
    
    mfi_overbought_count = sum(1 for result in analysis_results.values()
                             if 'error' not in result and result['latest_signal'] is not None
                             and result['latest_signal']['mfi'] > 70)
    
    macd_positive_count = sum(1 for result in analysis_results.values()
                            if 'error' not in result and result['latest_signal'] is not None
                            and result['latest_signal']['macd'] > 0)
    
    total_stocks = len([r for r in analysis_results.values() if 'error' not in r])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("MFI Oversold Stocks", mfi_oversold_count)
        
    with col2:
        st.metric("MFI Overbought Stocks", mfi_overbought_count)
        
    with col3:
        st.metric("MACD Positive", macd_positive_count)
    
    # Detailed insights
    st.write(f"• **{(mfi_oversold_count/total_stocks*100):.1f}%** of stocks are in oversold territory (MFI < 30)")
    st.write(f"• **{(mfi_overbought_count/total_stocks*100):.1f}%** of stocks are in overbought territory (MFI > 70)")
    st.write(f"• **{(macd_positive_count/total_stocks*100):.1f}%** of stocks have positive MACD")

def display_correlation_analysis(analysis_results):
    """Display correlation analysis."""
    
    st.subheader("🔗 Indicator Correlations")
    
    corr_chart = create_correlation_matrix(analysis_results)
    st.plotly_chart(corr_chart, use_container_width=True)

def display_all_signals(analysis_results):
    """Display all signals summary."""
    
    st.subheader("📋 Complete Signals Summary")
    
    all_signals = create_signals_summary(analysis_results)
    
    if not all_signals.empty:
        # Add filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            signal_filter = st.selectbox("Filter by Signal:", ["All", "BUY", "SELL", "HOLD"])
        
        with col2:
            min_strength = st.slider("Minimum Strength:", 0, 3, 0)
        
        with col3:
            sort_by = st.selectbox("Sort by:", ["Signal", "Strength", "Stock", "MFI", "Price"])
        
        # Apply filters
        filtered_df = all_signals.copy()
        
        if signal_filter != "All":
            filtered_df = filtered_df[filtered_df['Signal'] == signal_filter]
        
        filtered_df = filtered_df[filtered_df['Strength'] >= min_strength]
        
        if sort_by == "Strength":
            filtered_df = filtered_df.sort_values('Strength', ascending=False)
        elif sort_by in filtered_df.columns:
            filtered_df = filtered_df.sort_values(sort_by)
        
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        # Summary statistics
        st.subheader("📊 Summary Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Stocks", len(filtered_df))
        
        with col2:
            avg_strength = filtered_df['Strength'].mean() if len(filtered_df) > 0 else 0
            st.metric("Avg Signal Strength", f"{avg_strength:.2f}")
        
        with col3:
            doji_count = len(filtered_df[filtered_df['Is_Doji'] == '✓'])
            st.metric("Doji Patterns", doji_count)
        
        with col4:
            high_strength = len(filtered_df[filtered_df['Strength'] >= 2])
            st.metric("Strong Signals (≥2)", high_strength)
    
    else:
        st.info("No signal data available")

def display_individual_stock_analysis(analysis_results, stock_data):
    """Display individual stock analysis."""
    
    st.subheader("📊 Individual Stock Analysis")
    
    # Stock selection
    available_stocks = [stock for stock in analysis_results.keys() if 'error' not in analysis_results[stock]]
    
    if available_stocks:
        selected_stock = st.selectbox(
            "Select stock to analyze in detail:",
            options=available_stocks,
            index=0
        )
        
        if selected_stock and selected_stock in analysis_results:
            result = analysis_results[selected_stock]
            
            if 'error' not in result and not result['data'].empty:
                # Stock overview
                col1, col2, col3 = st.columns(3)
                
                latest_signal = result['latest_signal']
                stats = result['statistics']
                
                with col1:
                    signal_type = latest_signal['signal']
                    signal_strength = abs(latest_signal['strength'])
                    
                    if signal_type == 'BUY':
                        st.markdown(f"""
                        <div class="signal-buy">
                            <h3>🟢 {signal_type}</h3>
                            <p>Strength: {signal_strength}/3</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif signal_type == 'SELL':
                        st.markdown(f"""
                        <div class="signal-sell">
                            <h3>🔴 {signal_type}</h3>
                            <p>Strength: {signal_strength}/3</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="signal-neutral">
                            <h3>⚫ {signal_type}</h3>
                            <p>No Signal</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    st.metric("Current Price", f"₹{latest_signal['close_price']:.2f}")
                    st.metric("MFI", f"{latest_signal['mfi']:.1f}")
                
                with col3:
                    st.metric("MACD", f"{latest_signal['macd']:.4f}")
                    st.metric("Total Signals", stats['total_signals'])
                
                # Detailed chart
                stock_chart = create_individual_stock_chart(result['data'], selected_stock)
                st.plotly_chart(stock_chart, use_container_width=True)
                
                # Signal reason
                st.subheader("📝 Signal Analysis")
                st.write(f"**Reason:** {latest_signal['reason']}")
                
                # Statistics
                st.subheader("📊 Statistics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"• **Total Data Points:** {stats['data_points']}")
                    st.write(f"• **Signal Rate:** {stats['signal_rate']:.1f}%")
                    st.write(f"• **Average Signal Strength:** {stats['avg_signal_strength']:.2f}")
                
                with col2:
                    st.write(f"• **Buy Signals:** {stats['buy_signals']} ({stats['buy_rate']:.1f}%)")
                    st.write(f"• **Sell Signals:** {stats['sell_signals']} ({stats['sell_rate']:.1f}%)")
                    st.write(f"• **Doji Patterns:** {stats['doji_count']} ({stats['doji_rate']:.1f}%)")
            else:
                st.error(f"Error analyzing {selected_stock}: {result.get('error', 'Unknown error')}")
    else:
        st.info("No stocks available for individual analysis")

if __name__ == "__main__":
    main()
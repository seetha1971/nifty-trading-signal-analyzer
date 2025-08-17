# 🚀 Nifty 50 FNO Trading Signal Analyzer

A comprehensive trading signal analyzer for the top 50 Nifty 50 FNO (Futures & Options) stocks using advanced technical indicators including **Heikin Ashi Doji**, **MACD**, and **MFI**.

## ✨ Features

### 📊 Multi-Stock Analysis
- Analyze up to 50 Nifty 50 FNO stocks simultaneously
- Concurrent data fetching and processing for optimal performance
- Real-time signal generation and strength assessment

### 🔍 Advanced Technical Indicators

#### 1. **Heikin Ashi Doji Patterns**
- Identifies market indecision points
- Configurable threshold for Doji detection
- Visual marking on charts

#### 2. **MACD (Moving Average Convergence Divergence)**
- Bullish and bearish crossover detection
- Signal line analysis
- Histogram visualization

#### 3. **MFI (Money Flow Index)**
- Volume-weighted momentum indicator
- Configurable oversold/overbought levels
- Money flow analysis

### 🎯 Intelligent Signal Generation
- **Signal Strength Scoring**: 1-3 scale based on indicator confluence
- **Multi-condition Analysis**: Combines all three indicators for robust signals
- **Signal Prioritization**: Stronger signals override weaker ones

#### Signal Strength Levels:
- **Strength 3**: Doji + MFI extreme + MACD crossover
- **Strength 2**: Two indicators in confluence  
- **Strength 1**: Single strong indicator signal

### 📈 Comprehensive Visualizations

#### Portfolio Overview
- Signal distribution pie chart
- Portfolio-wide statistics
- Real-time signal counts

#### Sector Analysis
- Sector-wise signal breakdown
- Performance comparison across industries
- Industry-specific insights

#### Technical Analysis Charts
- Individual stock Heikin Ashi charts with signals
- MFI vs MACD scatter plots
- Signal strength heatmaps
- Indicator correlation matrices

#### Interactive Tables
- Sortable signal summaries
- Filterable by signal type and strength
- Export functionality (CSV)

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- Virtual environment (recommended)

### Quick Setup
```bash
# Clone and navigate to project
cd nifty_trading_signal_analyzer

# Create virtual environment
uv venv

# Activate environment
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### Dependencies
- `streamlit>=1.48.0` - Web application framework
- `yfinance>=0.2.65` - Yahoo Finance data fetching
- `pandas>=2.3.1` - Data manipulation
- `numpy>=2.3.2` - Numerical computing
- `plotly>=6.3.0` - Interactive visualizations
- `ta-lib>=0.6.5` - Technical analysis library
- `scikit-learn>=1.7.1` - Machine learning utilities

## 🚀 Running the Application

### Local Development
```bash
# Run the single-stock analyzer
streamlit run app.py --server.headless=true

# Run the multi-stock analyzer  
streamlit run nifty50_app.py --server.headless=true
```

### Production Deployment with Modal

#### Setup Modal (One-time)
```bash
# Install Modal
uv pip install modal

# Setup authentication
source .venv/bin/activate && modal setup
```

#### Deploy Multi-Stock Analyzer
```bash
modal deploy serve_nifty50_app.py
```

Your app will be available at: `https://[username]--nifty50-trading-analyzer-run.modal.run`

## 📊 How to Use

### 1. Configuration
- **Stock Selection**: Choose number of stocks to analyze (10-50)
- **Time Parameters**: Select period (1mo, 3mo, 6mo) and interval (15m, 1h, 1d)
- **Indicator Settings**: Adjust Doji threshold and MFI levels

### 2. Analysis Process
1. Click "Start Analysis" to begin
2. Data fetching progress will be displayed
3. Concurrent analysis of all selected stocks
4. Results displayed in comprehensive dashboard

### 3. Interpreting Results

#### Signal Types
- 🟢 **BUY**: Bullish confluence of indicators
- 🔴 **SELL**: Bearish confluence of indicators  
- ⚫ **HOLD**: No clear signal or conflicting indicators

#### Signal Strength
- **3/3**: Strong signal with all indicators aligned
- **2/3**: Medium signal with two indicators
- **1/3**: Weak signal with single indicator

### 4. Dashboard Sections

#### Portfolio Overview
- Real-time signal distribution
- Overall market sentiment
- Performance metrics

#### Top Signals
- Strongest BUY/SELL opportunities
- Ranked by signal strength
- Detailed reasoning for each signal

#### Sector Analysis  
- Industry-wise performance
- Sector rotation insights
- Comparative strength analysis

#### Individual Stock Analysis
- Detailed charts for specific stocks
- Complete indicator breakdown
- Historical signal performance

## 📈 Trading Strategy Framework

### Entry Signals
- **Strong BUY (3/3)**: High conviction long position
- **Medium BUY (2/3)**: Moderate position size
- **Weak BUY (1/3)**: Small exploratory position

### Exit Signals
- **Strong SELL (3/3)**: Exit long positions immediately
- **Medium SELL (2/3)**: Reduce position size
- **Weak SELL (1/3)**: Monitor closely, prepare to exit

### Risk Management
- Position size based on signal strength
- Stop losses below recent Doji lows
- Take profits at MFI overbought levels

## 🔍 Technical Implementation

### Data Processing Pipeline
1. **Concurrent Data Fetching**: Multi-threaded Yahoo Finance API calls
2. **Data Validation**: Quality checks and missing data handling
3. **Indicator Calculation**: Vectorized operations for performance
4. **Signal Generation**: Multi-condition logic with prioritization
5. **Visualization**: Real-time chart updates

### Performance Optimizations
- **Streamlit Caching**: 5-minute data cache for API efficiency
- **Concurrent Processing**: ThreadPoolExecutor for parallel analysis
- **Vectorized Calculations**: Pandas/NumPy operations
- **Selective Updates**: Only refresh changed data

### Architecture
```
nifty50_app.py              # Main Streamlit application
├── nifty50_stocks.py       # Stock symbols and sector mapping
├── multi_stock_fetcher.py  # Concurrent data fetching
├── multi_stock_analyzer.py # Signal analysis engine
├── multi_stock_visualizations.py # Chart generation
└── trading_indicators.py  # Technical indicator calculations
```

## 🎨 Customization

### Adding New Indicators
1. Implement calculation function in `trading_indicators.py`
2. Add to `calculate_all_indicators()` pipeline
3. Update signal generation logic
4. Create visualization in `multi_stock_visualizations.py`

### Modifying Signal Logic
Edit the `generate_trading_signals()` function to adjust:
- Indicator weights
- Confluence requirements  
- Signal strength thresholds
- Custom trading rules

### Styling and UI
- Modify CSS in `nifty50_app.py` for custom styling
- Update chart colors and themes in visualization modules
- Add new dashboard sections as needed

## 📊 Data Sources

- **Yahoo Finance**: Primary data source for OHLCV data
- **NSE Symbols**: All stocks use `.NS` suffix for NSE listings
- **Real-time Updates**: 15-minute delayed data (free tier)
- **Historical Data**: Up to 2 years of historical data

## ⚠️ Disclaimers

### Trading Risk Warning
- This tool is for educational and analytical purposes only
- Past performance does not guarantee future results
- Trading involves substantial risk of loss
- Always consult with financial advisors before trading

### Data Accuracy
- Data sourced from Yahoo Finance (15-minute delay)
- Technical indicators are approximations
- Market conditions can change rapidly
- Always verify signals with multiple sources

## 🤝 Contributing

### Development Setup
```bash
# Fork the repository
git clone [your-fork-url]
cd nifty_trading_signal_analyzer

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
streamlit run nifty50_app.py --server.headless=true

# Submit pull request
```

### Areas for Contribution
- Additional technical indicators
- Enhanced visualization options
- Backtesting capabilities
- Mobile-responsive design
- Performance optimizations

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Yahoo Finance API** for market data
- **Streamlit** for the web application framework
- **Plotly** for interactive visualizations
- **TA-Lib** for technical analysis functions

---

**Built with ❤️ for the Indian trading community**

*Happy Trading! 🚀📈*
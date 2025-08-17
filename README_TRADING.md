# NIFTY Trading Signal Analyzer 📈

A comprehensive trading application that analyzes NIFTY signals using advanced technical indicators on 15-minute timeframe data from Yahoo Finance.

## Features

### 🔍 Technical Indicators
- **Heikin-Ashi Candles**: Smoother price representation for trend analysis
- **Doji Detection**: Identifies indecision points in the market
- **Money Flow Index (MFI)**: Volume-weighted momentum indicator
- **MACD**: Moving Average Convergence Divergence with crossover signals

### 📊 Signal Analysis
- **Multi-factor Signal Generation**: Combines Doji, MFI, and MACD for robust signals
- **Signal Strength Classification**: 3-tier strength system (Weak, Medium, Strong)
- **Real-time Analysis**: Live data fetching and processing
- **Interactive Visualizations**: Advanced Plotly charts with signal overlays

### 📈 Dashboard Features
- Live NIFTY price tracking
- Interactive Heikin-Ashi candlestick charts
- Signal distribution analysis
- Performance metrics and correlation analysis
- Exportable signal history
- Configurable indicator parameters

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd nifty_trading_signal_analyzer
```

2. Set up virtual environment:
```bash
uv venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

## Usage

### Run Locally
```bash
streamlit run app.py --server.headless=true
```

### Deploy to Modal
```bash
modal setup  # One-time setup
modal deploy serve_streamlit.py
```

## Signal Logic

The application generates trading signals based on the following criteria:

### BUY Signals
- **Strong BUY (3)**: Doji + Oversold MFI + MACD Bullish Crossover
- **Medium BUY (2)**: Doji + Oversold MFI OR Doji + MACD Bullish
- **Weak BUY (1)**: Oversold MFI + MACD Bullish (no Doji)

### SELL Signals
- **Strong SELL (-3)**: Doji + Overbought MFI + MACD Bearish Crossover
- **Medium SELL (-2)**: Doji + Overbought MFI OR Doji + MACD Bearish
- **Weak SELL (-1)**: Overbought MFI + MACD Bearish (no Doji)

## Configuration

### Data Parameters
- **Time Period**: 1 Day to 2 Years
- **Time Interval**: 1 minute to 1 day (15 minutes recommended)

### Indicator Parameters
- **Doji Threshold**: 0.05 to 0.3 (default: 0.1)
- **MFI Oversold**: 10 to 40 (default: 30)
- **MFI Overbought**: 60 to 90 (default: 70)

## File Structure

```
nifty_trading_signal_analyzer/
├── app.py                    # Main Streamlit application
├── data_fetcher.py           # Yahoo Finance data fetching
├── trading_indicators.py     # Technical indicator calculations
├── visualizations.py         # Chart creation and visualization
├── serve_streamlit.py        # Modal deployment configuration
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Key Technical Details

### Heikin-Ashi Calculation
- HA_Close = (Open + High + Low + Close) / 4
- HA_Open = (Previous HA_Open + Previous HA_Close) / 2
- HA_High = max(High, HA_Open, HA_Close)
- HA_Low = min(Low, HA_Open, HA_Close)

### Doji Detection
- Body ratio = |HA_Close - HA_Open| / |HA_High - HA_Low|
- Doji when body ratio ≤ threshold (default: 0.1)

### MFI Calculation
- Typical Price = (High + Low + Close) / 3
- Money Flow = Typical Price × Volume
- MFI = 100 - (100 / (1 + Money Ratio))

### MACD Calculation
- MACD Line = EMA(12) - EMA(26)
- Signal Line = EMA(9) of MACD Line
- Histogram = MACD Line - Signal Line

## Screenshots

The application provides:
1. **Real-time NIFTY price dashboard** with current market metrics
2. **Interactive Heikin-Ashi charts** with overlaid trading signals
3. **Signal analysis tabs** for performance metrics and correlations
4. **Exportable signal history** for backtesting and analysis

## Disclaimer

This application is for educational and research purposes only. The trading signals generated should not be considered as financial advice. Always conduct your own research and consult with financial professionals before making investment decisions.

## License

This project is licensed under the MIT License.
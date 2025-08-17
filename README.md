# Nifty Trading Signal Analyzer

A comprehensive Streamlit web application for analyzing trading signals and technical indicators for Nifty 50 stocks and indices. This tool provides real-time data fetching, technical analysis, and interactive visualizations for Indian stock market data.

## Features

- **Real-time Data Fetching**: Get current stock prices and historical data using Yahoo Finance API
- **Technical Indicators**: Calculate and visualize various trading indicators including:
  - Simple Moving Averages (SMA)
  - Exponential Moving Averages (EMA)
  - Relative Strength Index (RSI)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - Stochastic Oscillator
- **Multi-Stock Analysis**: Compare multiple stocks simultaneously
- **Interactive Visualizations**: Dynamic charts with customizable parameters
- **Nifty 50 Integration**: Pre-configured with all Nifty 50 stocks

## Applications

### Main Applications
- `app.py`: General stock analysis dashboard
- `nifty50_app.py`: Specialized Nifty 50 analysis dashboard

### Core Modules
- `data_fetcher.py`: Stock data retrieval and caching
- `trading_indicators.py`: Technical indicator calculations
- `visualizations.py`: Chart generation and plotting
- `nifty50_stocks.py`: Nifty 50 stock configurations
- `multi_stock_analyzer.py`: Multi-stock comparison tools

## Requirements

- Python 3.11+
- uv (Python package manager)
- Modal account (for deployment)

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd nifty_trading_signal_analyzer
```

2. Create virtual environment:
```bash
uv venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

## Usage

### Local Development

Run the main application:
```bash
streamlit run app.py --server.headless=true
```

Run the Nifty 50 specific application:
```bash
streamlit run nifty50_app.py --server.headless=true
```

### Deployment to Modal

1. Setup Modal (one-time):
```bash
source .venv/bin/activate && modal setup
```

2. Deploy the application:
```bash
modal deploy serve_streamlit.py
```

Your app will be available at: `https://[username]--[app-name]-run.modal.run`

## Project Structure

```
├── app.py                      # Main Streamlit application
├── nifty50_app.py             # Nifty 50 specific dashboard
├── data_fetcher.py            # Data retrieval module
├── trading_indicators.py      # Technical analysis calculations
├── visualizations.py          # Plotting and chart generation
├── multi_stock_analyzer.py    # Multi-stock analysis tools
├── nifty50_stocks.py          # Nifty 50 stock definitions
├── serve_streamlit.py         # Modal deployment configuration
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Technical Indicators Supported

- **Trend Indicators**: SMA, EMA, MACD
- **Momentum Indicators**: RSI, Stochastic Oscillator
- **Volatility Indicators**: Bollinger Bands
- **Volume Analysis**: Volume-based indicators

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the web interface
- Deployed using [Modal](https://modal.com/) for serverless hosting
- Market data provided by Yahoo Finance API
- Technical analysis powered by pandas and numpy

---

🤖 Generated with [Memex](https://memex.tech)
Co-Authored-By: Memex <noreply@memex.tech>
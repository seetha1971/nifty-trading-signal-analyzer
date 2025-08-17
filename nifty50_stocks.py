"""
Nifty 50 Stocks Module
Contains the list of Nifty 50 stocks and their Yahoo Finance symbols for FNO trading.
"""

# Nifty 50 stocks with their Yahoo Finance symbols (NSE symbols with .NS suffix)
NIFTY50_STOCKS = {
    # Technology & IT Services
    'TCS': 'TCS.NS',
    'INFY': 'INFY.NS',
    'HCLTECH': 'HCLTECH.NS',
    'WIPRO': 'WIPRO.NS',
    'TECHM': 'TECHM.NS',
    'LTIM': 'LTIM.NS',
    
    # Financial Services & Banking
    'HDFCBANK': 'HDFCBANK.NS',
    'ICICIBANK': 'ICICIBANK.NS',
    'KOTAKBANK': 'KOTAKBANK.NS',
    'AXISBANK': 'AXISBANK.NS',
    'SBIN': 'SBIN.NS',
    'HDFCLIFE': 'HDFCLIFE.NS',
    'SBILIFE': 'SBILIFE.NS',
    'BAJFINANCE': 'BAJFINANCE.NS',
    'BAJAJFINSV': 'BAJAJFINSV.NS',
    
    # Consumer Goods & Retail
    'RELIANCE': 'RELIANCE.NS',
    'ITC': 'ITC.NS',
    'HINDUNILVR': 'HINDUNILVR.NS',
    'NESTLEIND': 'NESTLEIND.NS',
    'BRITANNIA': 'BRITANNIA.NS',
    'DABUR': 'DABUR.NS',
    'GODREJCP': 'GODREJCP.NS',
    'TATACONSUM': 'TATACONSUM.NS',
    
    # Automobiles
    'MARUTI': 'MARUTI.NS',
    'M&M': 'M&M.NS',
    'TATAMOTORS': 'TATAMOTORS.NS',
    'BAJAJ-AUTO': 'BAJAJ-AUTO.NS',
    'EICHERMOT': 'EICHERMOT.NS',
    'HEROMOTOCO': 'HEROMOTOCO.NS',
    
    # Pharmaceuticals
    'SUNPHARMA': 'SUNPHARMA.NS',
    'DRREDDY': 'DRREDDY.NS',
    'CIPLA': 'CIPLA.NS',
    'DIVISLAB': 'DIVISLAB.NS',
    'APOLLOHOSP': 'APOLLOHOSP.NS',
    
    # Metals & Mining
    'TATASTEEL': 'TATASTEEL.NS',
    'JSWSTEEL': 'JSWSTEEL.NS',
    'HINDALCO': 'HINDALCO.NS',
    'ADANIENT': 'ADANIENT.NS',
    'COALINDIA': 'COALINDIA.NS',
    
    # Energy & Power
    'ONGC': 'ONGC.NS',
    'POWERGRID': 'POWERGRID.NS',
    'NTPC': 'NTPC.NS',
    'BPCL': 'BPCL.NS',
    'IOC': 'IOC.NS',
    'ADANIPORTS': 'ADANIPORTS.NS',
    
    # Telecom & Media
    'BHARTIARTL': 'BHARTIARTL.NS',
    
    # Others
    'LT': 'LT.NS',
    'ULTRACEMCO': 'ULTRACEMCO.NS',
    'GRASIM': 'GRASIM.NS',
    'ASIANPAINT': 'ASIANPAINT.NS'
}

def get_nifty50_stocks():
    """
    Returns the dictionary of Nifty 50 stocks with their Yahoo Finance symbols.
    
    Returns:
        dict: Dictionary with stock names as keys and Yahoo Finance symbols as values
    """
    return NIFTY50_STOCKS

def get_top_fno_stocks(top_n: int = 50):
    """
    Get top N FNO stocks from Nifty 50.
    
    Args:
        top_n (int): Number of top stocks to return
        
    Returns:
        dict: Dictionary with top N stocks
    """
    stocks = get_nifty50_stocks()
    # Return top N stocks (all are FNO eligible in Nifty 50)
    return dict(list(stocks.items())[:min(top_n, len(stocks))])

def get_sector_wise_stocks():
    """
    Returns stocks grouped by sectors.
    
    Returns:
        dict: Dictionary with sectors as keys and stock lists as values
    """
    return {
        'Technology': ['TCS', 'INFY', 'HCLTECH', 'WIPRO', 'TECHM', 'LTIM'],
        'Banking & Financial Services': [
            'HDFCBANK', 'ICICIBANK', 'KOTAKBANK', 'AXISBANK', 'SBIN', 
            'HDFCLIFE', 'SBILIFE', 'BAJFINANCE', 'BAJAJFINSV'
        ],
        'Consumer Goods': [
            'RELIANCE', 'ITC', 'HINDUNILVR', 'NESTLEIND', 'BRITANNIA', 
            'DABUR', 'GODREJCP', 'TATACONSUM'
        ],
        'Automobiles': [
            'MARUTI', 'M&M', 'TATAMOTORS', 'BAJAJ-AUTO', 'EICHERMOT', 'HEROMOTOCO'
        ],
        'Pharmaceuticals': [
            'SUNPHARMA', 'DRREDDY', 'CIPLA', 'DIVISLAB', 'APOLLOHOSP'
        ],
        'Metals & Mining': [
            'TATASTEEL', 'JSWSTEEL', 'HINDALCO', 'ADANIENT', 'COALINDIA'
        ],
        'Energy & Power': [
            'ONGC', 'POWERGRID', 'NTPC', 'BPCL', 'IOC', 'ADANIPORTS'
        ],
        'Telecom': ['BHARTIARTL'],
        'Infrastructure & Others': ['LT', 'ULTRACEMCO', 'GRASIM', 'ASIANPAINT']
    }
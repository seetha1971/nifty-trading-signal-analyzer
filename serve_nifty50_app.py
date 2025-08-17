"""
Modal deployment script for Nifty 50 FNO Trading Signal Analyzer
"""

import shlex
import subprocess
from pathlib import Path
import modal

# Define container dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "streamlit~=1.35.0",
    "yfinance>=0.2.65",
    "pandas>=2.3.1", 
    "numpy>=2.3.2",
    "plotly>=6.3.0",
    "ta-lib>=0.6.5",
    "scikit-learn>=1.7.1"
)

app = modal.App(name="nifty50-trading-analyzer", image=image)

# Mount all necessary files
files_to_mount = [
    "nifty50_app.py",
    "nifty50_stocks.py",
    "multi_stock_fetcher.py",
    "multi_stock_analyzer.py", 
    "multi_stock_visualizations.py",
    "trading_indicators.py"
]

mounts = []
for file_name in files_to_mount:
    local_path = Path(__file__).parent / file_name
    remote_path = Path(f"/root/{file_name}")
    
    if local_path.exists():
        mounts.append(modal.Mount.from_local_file(local_path, remote_path))

@app.function(
    allow_concurrent_inputs=100,
    mounts=mounts,
)
@modal.web_server(8000)
def run():
    cmd = f"streamlit run /root/nifty50_app.py --server.port 8000 --server.enableCORS=false --server.enableXsrfProtection=false --server.headless=true"
    subprocess.Popen(shlex.split(cmd))

if __name__ == "__main__":
    app.serve()
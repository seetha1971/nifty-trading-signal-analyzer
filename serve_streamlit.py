import shlex
import subprocess
from pathlib import Path
import modal

# Define container dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "streamlit~=1.48.0",
    "yfinance~=0.2.65",
    "pandas~=2.3.1", 
    "numpy~=2.3.2",
    "plotly~=6.3.0",
    "ta-lib~=0.6.5",
    "scikit-learn~=1.7.1"
)

app = modal.App(name="nifty-trading-analyzer", image=image)

# Mount all Python files
app_files = [
    "app.py",
    "data_fetcher.py", 
    "trading_indicators.py",
    "visualizations.py"
]

mounts = []
for file in app_files:
    local_path = Path(__file__).parent / file
    remote_path = Path(f"/root/{file}")
    
    if not local_path.exists():
        raise RuntimeError(f"{file} not found! Ensure all required files are in the same directory.")
    
    mounts.append(modal.Mount.from_local_file(local_path, remote_path))

# Define the web server function
@app.function(
    allow_concurrent_inputs=100,
    mounts=mounts,
)
@modal.web_server(8000)
def run():
    cmd = f"streamlit run /root/app.py --server.port 8000 --server.enableCORS=false --server.enableXsrfProtection=false --server.headless=true"
    subprocess.Popen(shlex.split(cmd))

if __name__ == "__main__":
    app.serve()
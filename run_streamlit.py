import sys
from pathlib import Path
import streamlit.web.cli as stcli

# Path to the app file in the same folder
script = Path(__file__).resolve().parent / "advanced_app.py"

# Build argv exactly as if calling `streamlit run advanced_app.py --server.port=8501 --server.headless=true`
sys.argv = ["streamlit", "run", str(script), "--server.port=8501", "--server.headless=true"]

# Run Streamlit
if __name__ == "__main__":
    sys.exit(stcli.main())

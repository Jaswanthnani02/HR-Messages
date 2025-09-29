#!/usr/bin/env python3
"""
HR Messages Application Launcher
This script provides an easy way to run the HR Messages application.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'streamlit',
        'requests',
        'sqlite3'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("📦 Please install dependencies with: pip install -r requirements.txt")
        return False
    
    return True

def setup_environment():
    """Set up environment variables if .env file exists."""
    env_file = Path('.env')
    if env_file.exists():
        print("🔧 Loading environment variables from .env file")
        from dotenv import load_dotenv
        load_dotenv()
    else:
        print("ℹ️ No .env file found. Copy env.example to .env and configure your settings.")

def main():
    """Main application launcher."""
    print("🚀 Starting HR Messages Application...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Run the Streamlit app
    try:
        print("🌐 Launching Streamlit application...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "advanced_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

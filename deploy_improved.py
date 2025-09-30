#!/usr/bin/env python3
"""
Deployment script for the improved HR Messages application
Senior Code Review Implementation
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print deployment banner."""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║              🚀 HR Messages - Production Deployment         ║
    ║                    Senior Code Review Implementation         ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Check Python version compatibility."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install production dependencies."""
    print("\n📦 Installing production dependencies...")
    
    dependencies = [
        "streamlit>=1.37.0",
        "requests>=2.32.0",
        "pdfplumber>=0.11.4",
        "beautifulsoup4>=4.12.3",
        "python-dotenv>=1.1.1"
    ]
    
    try:
        for dep in dependencies:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        print("✅ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def setup_environment():
    """Set up production environment."""
    print("\n🔧 Setting up production environment...")
    
    # Create necessary directories
    directories = ['data', 'logs', 'backups', 'config']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create production configuration
    config_content = """# Production Configuration
GROQ_API_KEY=your_groq_api_key_here
DB_PATH=data/resume_vectors.db
LOG_LEVEL=INFO
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=txt,pdf
"""
    
    with open('.env.production', 'w') as f:
        f.write(config_content)
    print("✅ Created production configuration")
    
    # Create logging configuration
    logging_config = """[loggers]
keys=root,hr_messages

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_hr_messages]
level=INFO
handlers=consoleHandler,fileHandler
qualname=hr_messages
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=simpleFormatter
args=('logs/hr_messages.log',)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
"""
    
    with open('logging.conf', 'w') as f:
        f.write(logging_config)
    print("✅ Created logging configuration")

def create_production_script():
    """Create production startup script."""
    script_content = """#!/bin/bash
# HR Messages Production Startup Script

# Set environment
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Start the application
echo "🚀 Starting HR Messages Application..."
python app_improved.py
"""
    
    with open('start_production.sh', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Make executable on Unix systems
    if os.name != 'nt':
        os.chmod('start_production.sh', 0o755)
    
    print("✅ Created production startup script")

def create_docker_setup():
    """Create Docker configuration for production."""
    dockerfile_content = """FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p /app/data /app/logs /app/backups

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "app_improved.py", "--server.port=8501", "--server.address=0.0.0.0"]
"""
    
    with open('Dockerfile.production', 'w') as f:
        f.write(dockerfile_content)
    
    docker_compose_content = """version: '3.8'

services:
  hr-messages-prod:
    build:
      context: .
      dockerfile: Dockerfile.production
    ports:
      - "8501:8501"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - DB_PATH=/app/data/resume_vectors.db
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./.env.production:/app/.env:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
"""
    
    with open('docker-compose.production.yml', 'w') as f:
        f.write(docker_compose_content)
    
    print("✅ Created Docker configuration")

def create_monitoring_script():
    """Create monitoring and maintenance script."""
    monitoring_content = """#!/usr/bin/env python3
\"\"\"
HR Messages Application Monitoring Script
\"\"\"

import os
import sqlite3
import logging
from datetime import datetime, timedelta

def check_database_health():
    \"\"\"Check database health and performance.\"\"\"
    try:
        conn = sqlite3.connect('data/resume_vectors.db')
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='resumes'")
        if not cursor.fetchone():
            print("❌ Database table missing")
            return False
        
        # Check record count
        cursor.execute("SELECT COUNT(*) FROM resumes")
        count = cursor.fetchone()[0]
        print(f"✅ Database has {count} records")
        
        # Check recent activity
        cursor.execute("SELECT COUNT(*) FROM resumes WHERE created_at > datetime('now', '-7 days')")
        recent = cursor.fetchone()[0]
        print(f"✅ {recent} resumes added in last 7 days")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database health check failed: {e}")
        return False

def cleanup_old_data():
    \"\"\"Clean up old data and optimize database.\"\"\"
    try:
        conn = sqlite3.connect('data/resume_vectors.db')
        cursor = conn.cursor()
        
        # Clean up old records (older than 1 year)
        cursor.execute("DELETE FROM resumes WHERE created_at < datetime('now', '-1 year')")
        deleted = cursor.rowcount
        print(f"✅ Cleaned up {deleted} old records")
        
        # Optimize database
        cursor.execute("VACUUM")
        print("✅ Database optimized")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False

def main():
    print("🔍 HR Messages Application Health Check")
    print("=" * 50)
    
    # Check database
    if check_database_health():
        print("✅ Database is healthy")
    else:
        print("❌ Database issues detected")
    
    # Cleanup
    if cleanup_old_data():
        print("✅ Cleanup completed")
    else:
        print("❌ Cleanup failed")
    
    print("=" * 50)
    print("Health check completed")

if __name__ == "__main__":
    main()
"""
    
    with open('monitor.py', 'w') as f:
        f.write(monitoring_content)
    
    print("✅ Created monitoring script")

def main():
    """Main deployment function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Deployment failed at dependency installation")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Create production scripts
    create_production_script()
    create_docker_setup()
    create_monitoring_script()
    
    print("\n🎉 Production deployment completed successfully!")
    print("\n📋 Next steps:")
    print("1. Configure your environment variables in .env.production")
    print("2. Run: python app_improved.py")
    print("3. Or use Docker: docker-compose -f docker-compose.production.yml up")
    print("4. Monitor with: python monitor.py")
    print("\n📚 For more information, see SENIOR_CODE_REVIEW.md")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
TariffAI - Production Ready Enterprise Software
Run script for the FastAPI application
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """Main function to run the application"""
    
    # Add the app directory to Python path
    app_dir = Path(__file__).parent / "app"
    sys.path.insert(0, str(app_dir.parent))
    
    # Check if required directories exist
    data_dir = Path("data")
    logs_dir = Path("logs")
    
    data_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)
    
    print("🚢 Starting TariffAI - Intelligent HTS & Tariff Management")
    print("=" * 60)
    print("📁 Data directory:", data_dir.absolute())
    print("📁 Logs directory:", logs_dir.absolute())
    print("🌐 API Documentation: http://localhost:8000/api/docs")
    print("🌐 Frontend: http://localhost:3000")
    print("=" * 60)
    
    # Run the FastAPI application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()

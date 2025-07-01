#!/usr/bin/env python3
"""
TariffAI Startup Script
Simple script to start the application in different modes.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import chromadb
        import sentence_transformers
        print("✅ All Python dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False


def check_ollama():
    """Check if Ollama is running."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            if any('llama3.2:3b' in model.get('name', '') for model in models):
                print("✅ Ollama is running with llama3.2:3b model")
                return True
            else:
                print("⚠️ Ollama is running but llama3.2:3b model not found")
                print("Run: ollama pull llama3.2:3b")
                return False
        else:
            print("❌ Ollama is not responding")
            return False
    except Exception as e:
        print(f"❌ Ollama check failed: {e}")
        print("Please start Ollama: ollama serve")
        return False


def start_development():
    """Start the application in development mode."""
    print("🚀 Starting TariffAI in development mode...")
    
    if not check_dependencies():
        return False
    
    # Check Ollama (optional for development)
    ollama_available = check_ollama()
    if not ollama_available:
        print("⚠️ Continuing without Ollama - some features will be limited")
    
    # Set environment variables
    os.environ['ENVIRONMENT'] = 'development'
    os.environ['IS_DEVELOPMENT'] = 'true'
    
    # Start the application
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Development server stopped")
    except Exception as e:
        print(f"❌ Failed to start development server: {e}")
        return False
    
    return True


def start_production():
    """Start the application in production mode."""
    print("🚀 Starting TariffAI in production mode...")
    
    if not check_dependencies():
        return False
    
    if not check_ollama():
        return False
    
    # Set environment variables
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['IS_DEVELOPMENT'] = 'false'
    
    # Start the application
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--workers", "4"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Production server stopped")
    except Exception as e:
        print(f"❌ Failed to start production server: {e}")
        return False
    
    return True


def start_docker():
    """Start the application using Docker Compose."""
    print("🐳 Starting TariffAI with Docker Compose...")
    
    try:
        # Build and start services
        subprocess.run(["docker-compose", "up", "--build"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Docker services stopped")
    except FileNotFoundError:
        print("❌ Docker Compose not found. Please install Docker and Docker Compose.")
        return False
    except Exception as e:
        print(f"❌ Failed to start Docker services: {e}")
        return False
    
    return True


def setup_environment():
    """Setup the development environment."""
    print("🔧 Setting up TariffAI development environment...")
    
    # Create necessary directories
    directories = ['data', 'logs', 'data/chroma']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Check if data file exists
    data_file = Path("data/tariff_database_2025.xlsx")
    if not data_file.exists():
        print("⚠️ Tariff data file not found. Creating sample data...")
        # The application will create sample data automatically
    
    print("✅ Environment setup complete")


def main():
    parser = argparse.ArgumentParser(description="TariffAI Startup Script")
    parser.add_argument(
        "mode", 
        choices=["dev", "prod", "docker", "setup"],
        help="Startup mode"
    )
    parser.add_argument(
        "--no-check", 
        action="store_true",
        help="Skip dependency checks"
    )
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("🎯 TariffAI - Fresh Consolidated Edition")
    print("=" * 50)
    
    if args.mode == "setup":
        setup_environment()
    elif args.mode == "dev":
        if not args.no_check:
            setup_environment()
        start_development()
    elif args.mode == "prod":
        if not args.no_check:
            setup_environment()
        start_production()
    elif args.mode == "docker":
        start_docker()


if __name__ == "__main__":
    main() 
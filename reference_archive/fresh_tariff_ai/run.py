#!/usr/bin/env python3
"""
TariffAI Startup Script
Simple script to run the TariffAI application on Windows
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import chromadb
        import ollama
        print("✅ All core dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting TariffAI Backend...")
    
    # Change to the project directory
    os.chdir(Path(__file__).parent)
    
    # Start the backend server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped by user")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")

def start_frontend():
    """Start the frontend server"""
    print("🌐 Starting TariffAI Frontend...")
    
    # Change to the frontend directory
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    # Start a simple HTTP server
    try:
        subprocess.run([
            sys.executable, "-m", "http.server", "3000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped by user")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")

def main():
    """Main startup function"""
    print("🎯 TariffAI - Fresh Consolidated Edition")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    print("\n📋 Available options:")
    print("1. Start Backend only")
    print("2. Start Frontend only") 
    print("3. Start Both (Backend + Frontend)")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        start_backend()
    elif choice == "2":
        start_frontend()
    elif choice == "3":
        print("⚠️  Starting both services...")
        print("   Backend will be available at: http://localhost:8000")
        print("   Frontend will be available at: http://localhost:3000")
        print("   Press Ctrl+C to stop both services")
        
        # Start backend in background
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], cwd=Path(__file__).parent)
        
        # Wait a moment for backend to start
        time.sleep(3)
        
        # Start frontend
        frontend_dir = Path(__file__).parent / "frontend"
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "http.server", "3000"
        ], cwd=frontend_dir)
        
        try:
            # Open browser
            webbrowser.open("http://localhost:3000")
            
            # Wait for user to stop
            print("✅ Both services are running!")
            print("   Press Ctrl+C to stop...")
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            backend_process.terminate()
            frontend_process.terminate()
            print("✅ Services stopped")
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 
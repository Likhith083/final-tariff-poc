#!/usr/bin/env python3
"""
ATLAS Enterprise Demo Startup Script
Starts both backend and frontend servers for demonstration
"""

import subprocess
import time
import sys
import os
from pathlib import Path
import threading
import signal

def run_backend():
    """Start the backend server"""
    print("🚀 Starting ATLAS Backend...")
    backend_dir = Path(__file__).parent / "backend"
    
    try:
        # Change to backend directory and start server
        os.chdir(backend_dir)
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main_unified:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except Exception as e:
        print(f"❌ Backend error: {e}")

def run_frontend():
    """Start the frontend server"""
    print("🎨 Starting ATLAS Frontend...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    try:
        # Change to frontend directory and start server
        os.chdir(frontend_dir)
        subprocess.run(["npm", "run", "dev"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
    except Exception as e:
        print(f"❌ Frontend error: {e}")

def check_ollama():
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running")
            return True
        else:
            print("⚠️  Ollama is not responding properly")
            return False
    except Exception:
        print("❌ Ollama is not running. Please start it with: ollama serve")
        return False

def main():
    """Main function to start the demo"""
    print("=" * 60)
    print("🌟 ATLAS Enterprise - Demo Startup")
    print("=" * 60)
    
    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    
    # Check if we're in the right directory
    if not (Path.cwd() / "backend" / "main_unified.py").exists():
        print("❌ Please run this script from the atlas-enterprise directory")
        sys.exit(1)
    
    # Check Ollama
    ollama_running = check_ollama()
    if not ollama_running:
        print("🔧 You can start Ollama in another terminal with: ollama serve")
        print("   (AI features will be limited without Ollama)")
    
    print("\n🚀 Starting ATLAS Enterprise Demo...")
    print("📍 Backend will be available at: http://localhost:8000")
    print("📍 Frontend will be available at: http://localhost:3000")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("\n⌨️  Press Ctrl+C to stop all servers\n")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Wait a bit for backend to start
    time.sleep(3)
    
    # Start frontend in main thread
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down ATLAS Enterprise Demo...")
        print("✅ Demo stopped successfully")

if __name__ == "__main__":
    main() 
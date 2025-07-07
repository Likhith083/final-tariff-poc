#!/usr/bin/env python3
"""
ATLAS Startup Script
Easily start both backend and frontend services
"""
import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("🚢 ATLAS - Intelligent HTS & Tariff Management")
    print("=" * 60)
    print("Starting consolidated tariff management system...")
    print()

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Node.js is not installed")
            return False
        print(f"✅ Node.js: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Node.js is not installed")
        return False
    
    # Check npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ npm is not installed")
            return False
        print(f"✅ npm: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ npm is not installed")
        return False
    
    print("✅ All dependencies are available")
    return True

def install_backend_dependencies():
    """Install backend Python dependencies"""
    print("\n📦 Installing backend dependencies...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Check if virtual environment exists
    venv_dir = backend_dir / "venv"
    if not venv_dir.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], cwd=backend_dir)
    
    # Install requirements
    pip_cmd = str(venv_dir / "Scripts" / "pip.exe") if os.name == 'nt' else str(venv_dir / "bin" / "pip")
    requirements_file = backend_dir / "requirements.txt"
    
    if requirements_file.exists():
        print("Installing Python packages...")
        result = subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], cwd=backend_dir)
        if result.returncode != 0:
            print("❌ Failed to install backend dependencies")
            return False
        print("✅ Backend dependencies installed")
    else:
        print("⚠️ No requirements.txt found in backend directory")
    
    return True

def install_frontend_dependencies():
    """Install frontend Node.js dependencies"""
    print("\n📦 Installing frontend dependencies...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print("❌ package.json not found in frontend directory")
        return False
    
    print("Installing Node.js packages...")
    result = subprocess.run(["npm", "install"], cwd=frontend_dir)
    if result.returncode != 0:
        print("❌ Failed to install frontend dependencies")
        return False
    
    print("✅ Frontend dependencies installed")
    return True

def start_backend():
    """Start the backend server"""
    print("\n🚀 Starting backend server...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return None
    
    # Activate virtual environment and start server
    if os.name == 'nt':  # Windows
        python_cmd = str(backend_dir / "venv" / "Scripts" / "python.exe")
    else:  # Unix/Linux/Mac
        python_cmd = str(backend_dir / "venv" / "bin" / "python")
    
    try:
        # Start backend in background
        process = subprocess.Popen(
            [python_cmd, "main.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Backend server started on http://localhost:8000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Backend failed to start: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend():
    """Start the frontend development server"""
    print("\n🚀 Starting frontend server...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None
    
    try:
        # Start frontend in background
        process = subprocess.Popen(
            ["npm", "start"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for server to start
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Frontend server started on http://localhost:3000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Frontend failed to start: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def open_browser():
    """Open browser to the application"""
    print("\n🌐 Opening browser...")
    time.sleep(2)
    try:
        webbrowser.open("http://localhost:3000")
        print("✅ Browser opened to ATLAS")
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print("Please manually open http://localhost:3000")

def main():
    """Main startup function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install required dependencies.")
        sys.exit(1)
    
    # Install dependencies
    if not install_backend_dependencies():
        print("\n❌ Backend dependency installation failed.")
        sys.exit(1)
    
    if not install_frontend_dependencies():
        print("\n❌ Frontend dependency installation failed.")
        sys.exit(1)
    
    # Start services
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ Failed to start backend. Exiting.")
        sys.exit(1)
    
    frontend_process = start_frontend()
    if not frontend_process:
        print("\n❌ Failed to start frontend. Stopping backend.")
        backend_process.terminate()
        sys.exit(1)
    
    # Open browser
    open_browser()
    
    print("\n" + "=" * 60)
    print("🎉 ATLAS is now running!")
    print("=" * 60)
    print("📱 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all services")
    print("=" * 60)
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("\n❌ Backend process stopped unexpectedly")
                break
                
            if frontend_process.poll() is not None:
                print("\n❌ Frontend process stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping services...")
        
        # Stop processes
        if backend_process:
            backend_process.terminate()
            print("✅ Backend stopped")
        
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend stopped")
        
        print("\n👋 ATLAS stopped. Goodbye!")

if __name__ == "__main__":
    main() 
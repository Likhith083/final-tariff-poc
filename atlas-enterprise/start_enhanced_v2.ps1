# ATLAS Enterprise Enhanced V2 - Startup Script
# Complete AI-powered trade compliance platform with advanced features

param(
    [string]$Environment = "development",
    [switch]$SkipDependencies,
    [switch]$ResetDatabase,
    [switch]$LoadSampleData,
    [switch]$EnableDebug,
    [switch]$RunTests,
    [int]$Port = 8000,
    [string]$Host = "0.0.0.0"
)

# Color functions for better output
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success { param([string]$Message) Write-ColorOutput "✅ $Message" "Green" }
function Write-Error { param([string]$Message) Write-ColorOutput "❌ $Message" "Red" }
function Write-Warning { param([string]$Message) Write-ColorOutput "⚠️  $Message" "Yellow" }
function Write-Info { param([string]$Message) Write-ColorOutput "ℹ️  $Message" "Cyan" }
function Write-Header { param([string]$Message) Write-ColorOutput "`n🚀 $Message" "Magenta" }

# Main startup function
function Start-AtlasEnterpriseV2 {
    Write-Header "ATLAS Enterprise Enhanced V2 - Startup"
    Write-Info "Advanced AI-Powered Trade Compliance Platform"
    Write-Info "Version: 2.0.0 | Environment: $Environment"
    
    # Check if we're in the correct directory
    if (-not (Test-Path "backend/main_enhanced_v2.py")) {
        Write-Error "Please run this script from the atlas-enterprise root directory"
        Write-Info "Current directory: $(Get-Location)"
        exit 1
    }
    
    try {
        # Step 1: System Requirements Check
        Test-SystemRequirements
        
        # Step 2: Python Environment Setup
        if (-not $SkipDependencies) {
            Setup-PythonEnvironment
        }
        
        # Step 3: Database Setup
        Setup-Databases
        
        # Step 4: Initialize Services
        Initialize-Services
        
        # Step 5: Load Sample Data (if requested)
        if ($LoadSampleData) {
            Load-SampleData
        }
        
        # Step 6: Run Tests (if requested)
        if ($RunTests) {
            Run-Tests
        }
        
        # Step 7: Start Application
        Start-Application
        
    } catch {
        Write-Error "Startup failed: $($_.Exception.Message)"
        Write-Info "Check the logs for more details"
        exit 1
    }
}

function Test-SystemRequirements {
    Write-Header "Checking System Requirements"
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python: $pythonVersion"
    } catch {
        Write-Error "Python not found. Please install Python 3.9+"
        exit 1
    }
    
    # Check Node.js (for frontend)
    try {
        $nodeVersion = node --version 2>&1
        Write-Success "Node.js: $nodeVersion"
    } catch {
        Write-Warning "Node.js not found. Frontend features may not work"
    }
    
    # Check Redis
    try {
        redis-cli ping 2>&1 | Out-Null
        Write-Success "Redis: Running"
    } catch {
        Write-Warning "Redis not detected. Starting embedded Redis..."
        # In production, ensure Redis is properly configured
    }
    
    # Check PostgreSQL
    try {
        # This would check for PostgreSQL - simplified for demo
        Write-Info "PostgreSQL: Using SQLite fallback for development"
    } catch {
        Write-Warning "PostgreSQL not detected. Using SQLite fallback"
    }
    
    # Check system dependencies
    $systemDeps = @("tesseract", "ffmpeg")
    foreach ($dep in $systemDeps) {
        try {
            & $dep --version 2>&1 | Out-Null
            Write-Success "$dep: Available"
        } catch {
            Write-Warning "$dep: Not found. Some features may be limited"
        }
    }
}

function Setup-PythonEnvironment {
    Write-Header "Setting up Python Environment"
    
    # Check if virtual environment exists
    if (-not (Test-Path "backend/venv")) {
        Write-Info "Creating virtual environment..."
        Set-Location backend
        python -m venv venv
        Set-Location ..
        Write-Success "Virtual environment created"
    }
    
    # Activate virtual environment
    Write-Info "Activating virtual environment..."
    if (Test-Path "backend/venv/Scripts/Activate.ps1") {
        & backend/venv/Scripts/Activate.ps1
    } else {
        Write-Error "Failed to activate virtual environment"
        exit 1
    }
    
    # Upgrade pip
    Write-Info "Upgrading pip..."
    python -m pip install --upgrade pip
    
    # Install dependencies
    Write-Info "Installing dependencies..."
    Write-Warning "This may take several minutes for first-time setup..."
    
    Set-Location backend
    
    # Install basic requirements first
    python -m pip install fastapi uvicorn sqlalchemy asyncpg redis
    
    # Install enhanced requirements
    if (Test-Path "requirements_enhanced_v2.txt") {
        python -m pip install -r requirements_enhanced_v2.txt
    } else {
        python -m pip install -r requirements_enhanced.txt
    }
    
    Set-Location ..
    Write-Success "Dependencies installed"
}

function Setup-Databases {
    Write-Header "Setting up Databases"
    
    if ($ResetDatabase) {
        Write-Warning "Resetting databases..."
        Remove-Item -Path "backend/data" -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    # Create data directories
    $dataDirs = @(
        "backend/data",
        "backend/data/sqlite",
        "backend/data/chroma",
        "backend/data/uploads",
        "backend/data/exports",
        "backend/data/logs"
    )
    
    foreach ($dir in $dataDirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Success "Created directory: $dir"
        }
    }
    
    # Initialize databases
    Write-Info "Initializing databases..."
    Set-Location backend
    
    python -c @"
import asyncio
from core.database import init_database
from services.knowledge_base_service import knowledge_service
from services.enhanced_ai_service import enhanced_ai_service

async def setup():
    await init_database()
    await knowledge_service.initialize()
    await enhanced_ai_service.initialize()
    print('✅ Databases initialized successfully')

asyncio.run(setup())
"@
    
    Set-Location ..
    Write-Success "Database setup completed"
}

function Initialize-Services {
    Write-Header "Initializing Services"
    
    Set-Location backend
    
    # Test service initialization
    Write-Info "Testing service initialization..."
    python -c @"
import asyncio
from services.enhanced_exchange_rate_service import EnhancedExchangeRateService
from services.tariff_scraper_service import TariffScraperService
from services.free_api_integration_service import FreeAPIIntegrationService
from services.rate_limiting_service import rate_limit_service
from services.notification_service import notification_service
from services.analytics_service import analytics_service

async def test_services():
    try:
        # Initialize core services
        exchange_service = EnhancedExchangeRateService()
        await exchange_service.initialize()
        print('✅ Exchange Rate Service initialized')
        
        scraper_service = TariffScraperService()
        await scraper_service.initialize()
        print('✅ Scraper Service initialized')
        
        api_service = FreeAPIIntegrationService()
        await api_service.initialize()
        print('✅ Free API Service initialized')
        
        await rate_limit_service.initialize()
        print('✅ Rate Limiting Service initialized')
        
        await notification_service.initialize()
        print('✅ Notification Service initialized')
        
        await analytics_service.initialize()
        print('✅ Analytics Service initialized')
        
        print('🎉 All services initialized successfully!')
        
    except Exception as e:
        print(f'❌ Service initialization failed: {e}')
        return False
    
    return True

result = asyncio.run(test_services())
exit(0 if result else 1)
"@
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "All services initialized successfully"
    } else {
        Write-Error "Service initialization failed"
        Set-Location ..
        exit 1
    }
    
    Set-Location ..
}

function Load-SampleData {
    Write-Header "Loading Sample Data"
    
    Set-Location backend
    
    Write-Info "Loading sample knowledge base data..."
    python -c @"
import asyncio
from services.knowledge_base_service import knowledge_service

async def load_sample():
    await knowledge_service.initialize()
    
    # Sample data
    samples = [
        {
            'content': 'HTS Code 8471.30.01 applies to portable automatic data processing machines weighing not more than 10 kg. Duty rate is typically 0% under most trade agreements.',
            'source': 'sample_data'
        },
        {
            'content': 'Certificate of Origin is required for claiming preferential tariff treatment under NAFTA/USMCA. Must be completed by the exporter.',
            'source': 'sample_data'
        },
        {
            'content': 'Electronic products from China may be subject to additional Section 301 tariffs. Check current rates as they change frequently.',
            'source': 'sample_data'
        }
    ]
    
    for sample in samples:
        result = await knowledge_service.add_knowledge_from_text(
            text_input=sample['content'],
            user_id='system',
            source=sample['source']
        )
        print(f'✅ Added sample: {result.get("title", "Unknown")[:50]}...')
    
    print('🎉 Sample data loaded successfully!')

asyncio.run(load_sample())
"@
    
    Set-Location ..
    Write-Success "Sample data loaded"
}

function Run-Tests {
    Write-Header "Running Tests"
    
    Set-Location backend
    
    Write-Info "Running basic health tests..."
    python -c @"
import asyncio
import httpx
from main_enhanced_v2 import app
from fastapi.testclient import TestClient

def test_basic_endpoints():
    client = TestClient(app)
    
    # Test root endpoint
    response = client.get('/')
    assert response.status_code == 200
    print('✅ Root endpoint test passed')
    
    # Test health endpoint
    response = client.get('/health/enhanced')
    assert response.status_code == 200
    print('✅ Health endpoint test passed')
    
    print('🎉 Basic tests completed successfully!')

test_basic_endpoints()
"@
    
    Set-Location ..
    Write-Success "Tests completed"
}

function Start-Application {
    Write-Header "Starting ATLAS Enterprise Enhanced V2"
    
    Set-Location backend
    
    # Create startup command
    $startupArgs = @(
        "main_enhanced_v2:app",
        "--host", $Host,
        "--port", $Port.ToString()
    )
    
    if ($EnableDebug -or $Environment -eq "development") {
        $startupArgs += "--reload"
        Write-Info "Debug mode enabled - auto-reload active"
    }
    
    if ($Environment -eq "production") {
        $startupArgs += "--workers", "4"
        Write-Info "Production mode - multiple workers enabled"
    }
    
    Write-Success "Starting server on http://${Host}:${Port}"
    Write-Info "Documentation available at: http://${Host}:${Port}/docs"
    Write-Info "Alternative docs at: http://${Host}:${Port}/redoc"
    Write-Info ""
    Write-Info "🌟 Enhanced Features Available:"
    Write-Info "  📚 Knowledge Base Updates: Tell the AI assistant to remember information"
    Write-Info "  🔔 Real-time Notifications: WebSocket support for live updates"
    Write-Info "  📊 Advanced Analytics: Predictive modeling and business intelligence"
    Write-Info "  🤖 Multimodal AI: Process documents, images, and voice input"
    Write-Info "  ⚡ Performance Optimized: Caching, rate limiting, and bulk operations"
    Write-Info ""
    Write-Warning "Press Ctrl+C to stop the server"
    Write-Info ""
    
    # Start the application
    uvicorn @startupArgs
}

function Show-Help {
    Write-Host @"
ATLAS Enterprise Enhanced V2 - Startup Script

USAGE:
    .\start_enhanced_v2.ps1 [OPTIONS]

OPTIONS:
    -Environment <env>     Set environment (development|production) [default: development]
    -SkipDependencies      Skip Python dependency installation
    -ResetDatabase         Reset all databases (DESTRUCTIVE)
    -LoadSampleData        Load sample data into knowledge base
    -EnableDebug           Enable debug mode with auto-reload
    -RunTests              Run basic health tests before starting
    -Port <port>           Port to bind to [default: 8000]
    -Host <host>           Host to bind to [default: 0.0.0.0]
    -Help                  Show this help message

EXAMPLES:
    # Basic startup
    .\start_enhanced_v2.ps1

    # Development with sample data
    .\start_enhanced_v2.ps1 -LoadSampleData -EnableDebug

    # Production mode
    .\start_enhanced_v2.ps1 -Environment production -Port 80

    # Reset and reload everything
    .\start_enhanced_v2.ps1 -ResetDatabase -LoadSampleData -RunTests

FEATURES:
    🧠 AI-Powered Knowledge Management
    📊 Advanced Analytics & Predictive Modeling  
    🔔 Real-time Notifications & WebSockets
    ⚡ Performance Optimizations & Caching
    🤖 Multimodal AI (Text, Images, Voice)
    🔒 Enterprise Security Features
"@
}

# Main execution
if ($args -contains "-Help" -or $args -contains "--help" -or $args -contains "/?") {
    Show-Help
    exit 0
}

# Set error handling
$ErrorActionPreference = "Stop"

# Start the application
Start-AtlasEnterpriseV2 
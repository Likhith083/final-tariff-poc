# ATLAS Enterprise Enhanced Startup Script
# Starts the advanced tariff calculator with all enhanced services

Write-Host "🚀 Starting ATLAS Enterprise Enhanced Tariff Calculator" -ForegroundColor Green
Write-Host "=" * 80

# Check if we're in the correct directory
if (-not (Test-Path "atlas-enterprise")) {
    Write-Host "❌ Please run this script from the ATLAS root directory" -ForegroundColor Red
    exit 1
}

Set-Location atlas-enterprise

# Install enhanced backend dependencies
Write-Host "📦 Installing enhanced backend dependencies..." -ForegroundColor Cyan
Set-Location backend
if (Test-Path "requirements_enhanced.txt") {
    pip install -r requirements_enhanced.txt
    Write-Host "✅ Enhanced dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠️ Using standard requirements.txt" -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Initialize databases for enhanced services
Write-Host "🗄️ Initializing enhanced databases..." -ForegroundColor Cyan
python -c "
try:
    import sys
    sys.path.append('.')
    
    # Initialize all enhanced services
    from services.enhanced_exchange_rate_service import EnhancedExchangeRateService
    enhanced_exchange = EnhancedExchangeRateService()
    print('✅ Enhanced exchange rate service initialized')
    
    from services.tariff_scraper_service import TariffScraperService  
    scraper = TariffScraperService()
    print('✅ Tariff scraper service initialized')
    
    from services.free_api_integration_service import FreeAPIIntegrationService
    free_apis = FreeAPIIntegrationService()
    print('✅ Free API integration service initialized')
    
    from agents.tariff_intelligence_agent import TariffIntelligenceAgent
    intelligence = TariffIntelligenceAgent()
    print('✅ Intelligence agent system initialized')
    
    print('🎯 All enhanced services ready!')
    
except ImportError as e:
    print(f'⚠️ Some enhanced features may not be available: {e}')
    print('🔄 Falling back to standard services')
except Exception as e:
    print(f'❌ Initialization error: {e}')
"

Set-Location ..

# Start enhanced backend
Write-Host "🔧 Starting enhanced backend server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; if (Test-Path 'main_enhanced.py') { python main_enhanced.py } else { python main_unified.py }" -WindowStyle Normal

# Wait for backend to start
Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test backend health
Write-Host "🏥 Checking backend health..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get -TimeoutSec 10
    Write-Host "✅ Backend is running: $($response.name) v$($response.version)" -ForegroundColor Green
    
    # Test enhanced features
    if ($response.version -eq "2.0.0") {
        Write-Host "🎯 Enhanced features detected!" -ForegroundColor Green
        Write-Host "  • Advanced Currency Exchange with Predictive Analytics" -ForegroundColor Cyan
        Write-Host "  • Real-time Web Scraping from Government Sources" -ForegroundColor Cyan
        Write-Host "  • AI-Powered Product Classification" -ForegroundColor Cyan
        Write-Host "  • Agentic Intelligence Framework" -ForegroundColor Cyan
        Write-Host "  • Free API Integration (UN Comtrade, World Bank, OECD)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "⚠️ Backend health check failed, but it may still be starting up" -ForegroundColor Yellow
}

# Start frontend
Write-Host "🎨 Starting frontend development server..." -ForegroundColor Cyan
Set-Location frontend

# Install frontend dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Cyan
    npm install
}

# Start frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev" -WindowStyle Normal

# Wait for frontend to start
Write-Host "⏳ Waiting for frontend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Set-Location ..

# Display access information
Write-Host ""
Write-Host "🎉 ATLAS Enterprise Enhanced is now running!" -ForegroundColor Green
Write-Host "=" * 80
Write-Host "📍 Access URLs:" -ForegroundColor Cyan
Write-Host "  Frontend:          http://localhost:3000" -ForegroundColor White
Write-Host "  Backend API:       http://localhost:8000" -ForegroundColor White
Write-Host "  API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Health Check:      http://localhost:8000/api/v1/system/health" -ForegroundColor White

Write-Host ""
Write-Host "🚀 Enhanced Features Available:" -ForegroundColor Cyan
Write-Host "  • Enhanced Exchange Rates:     /api/v1/exchange/enhanced/" -ForegroundColor White
Write-Host "  • Web Scraping:                /api/v1/scraper/" -ForegroundColor White
Write-Host "  • Free API Integration:        /api/v1/free-apis/" -ForegroundColor White
Write-Host "  • Intelligence Agents:         /api/v1/intelligence/" -ForegroundColor White
Write-Host "  • Enhanced Calculations:       /api/v1/tariff/enhanced-calculate" -ForegroundColor White

Write-Host ""
Write-Host "🔍 To run the complete demo:" -ForegroundColor Cyan
Write-Host "  python proof_of_concept_demo.py" -ForegroundColor White

Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "  • Implementation Guide:        ADVANCED_IMPLEMENTATION_GUIDE.md" -ForegroundColor White
Write-Host "  • Enhanced Features Analysis:  ENHANCED_FEATURES_ANALYSIS.md" -ForegroundColor White

Write-Host ""
Write-Host "⚡ Pro Tips:" -ForegroundColor Yellow
Write-Host "  • All new features are backward compatible" -ForegroundColor White
Write-Host "  • AI models will download on first use (may take time)" -ForegroundColor White  
Write-Host "  • Background services auto-update data every 4-6 hours" -ForegroundColor White
Write-Host "  • Check system health at /api/v1/system/health" -ForegroundColor White

Write-Host ""
Write-Host "🛑 To stop services:" -ForegroundColor Red
Write-Host "  Close the PowerShell windows or press Ctrl+C" -ForegroundColor White

Write-Host ""
Write-Host "✨ Enjoy your enhanced ATLAS Enterprise experience!" -ForegroundColor Green
Write-Host "=" * 80 
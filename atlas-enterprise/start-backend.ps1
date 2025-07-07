# Start ATLAS Backend
Write-Host "🚀 Starting ATLAS Backend..." -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "backend\main_unified.py")) {
    Write-Host "❌ Please run this script from the atlas-enterprise directory" -ForegroundColor Red
    exit 1
}

# Change to backend directory and start
Set-Location backend
Write-Host "📍 Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

python main_unified.py 
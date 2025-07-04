# =============================================================================
# TariffAI Development Environment Starter
# =============================================================================

Write-Host "🚢 Starting TariffAI Development Environment..." -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item "env.example" ".env"
    Write-Host "✅ .env file created. Please review and update if needed." -ForegroundColor Green
}

# Start the development environment
Write-Host "🚀 Starting all services with Docker Compose..." -ForegroundColor Cyan
Write-Host ""

try {
    docker-compose up --build
} catch {
    Write-Host "❌ Failed to start services. Please check the error above." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 TariffAI is now running!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "🔧 Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "🔍 ChromaDB: http://localhost:8001" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow 
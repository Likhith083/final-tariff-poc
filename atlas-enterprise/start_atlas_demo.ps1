# ATLAS Enterprise Demo Startup Script - PowerShell Version
# Starts both backend and frontend servers for demonstration

Write-Host "=" -ForegroundColor Blue -NoNewline
Write-Host ("=" * 59) -ForegroundColor Blue
Write-Host "🌟 ATLAS Enterprise - Demo Startup" -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Blue -NoNewline
Write-Host ("=" * 59) -ForegroundColor Blue

Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Yellow

# Check if we're in the right directory
if (-not (Test-Path "backend\main_unified.py")) {
    Write-Host "❌ Please run this script from the atlas-enterprise directory" -ForegroundColor Red
    exit 1
}

# Check Ollama
Write-Host "🤖 Checking Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Ollama is running" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Ollama is not running. Please start it with: ollama serve" -ForegroundColor Red
    Write-Host "🔧 You can start Ollama in another terminal with: ollama serve" -ForegroundColor Yellow
    Write-Host "   (AI features will be limited without Ollama)" -ForegroundColor Yellow
}

Write-Host "`n🚀 Starting ATLAS Enterprise Demo..." -ForegroundColor Green
Write-Host "📍 Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📍 Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "📍 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "`n⌨️  Press Ctrl+C to stop all servers`n" -ForegroundColor Yellow

# Start backend in background
Write-Host "🚀 Starting ATLAS Backend..." -ForegroundColor Green
Set-Location backend
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python main_unified.py
}

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "🎨 Starting ATLAS Frontend..." -ForegroundColor Green
Set-Location ..\frontend

try {
    npm run dev
} catch {
    Write-Host "`n🛑 Frontend startup interrupted" -ForegroundColor Red
} finally {
    Write-Host "`n🛑 Shutting down ATLAS Enterprise Demo..." -ForegroundColor Yellow
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    Write-Host "✅ Demo stopped successfully" -ForegroundColor Green
} 
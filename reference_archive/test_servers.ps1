# Test Script for TariffAI Servers
Write-Host "🔍 Testing TariffAI Servers..." -ForegroundColor Cyan
Write-Host ""

# Test Backend
Write-Host "Testing Backend (http://localhost:8000)..." -ForegroundColor Yellow
try {
    $backendResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5
    if ($backendResponse.StatusCode -eq 200) {
        Write-Host "✅ Backend is RUNNING" -ForegroundColor Green
        Write-Host "   Health Check: $($backendResponse.Content)" -ForegroundColor Gray
        Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Blue
    } else {
        Write-Host "❌ Backend returned status: $($backendResponse.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Backend is NOT RUNNING" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
}

Write-Host ""

# Test Frontend
Write-Host "Testing Frontend (http://localhost:3000)..." -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -TimeoutSec 5
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "✅ Frontend is RUNNING" -ForegroundColor Green
        Write-Host "   URL: http://localhost:3000" -ForegroundColor Blue
    } else {
        Write-Host "❌ Frontend returned status: $($frontendResponse.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Frontend is NOT RUNNING" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🎯 Summary:" -ForegroundColor Cyan
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "📝 To start servers manually:" -ForegroundColor Cyan
Write-Host "   Backend:  cd backend && .venv\Scripts\Activate.ps1 && python main.py" -ForegroundColor Gray
Write-Host "   Frontend: cd frontend && npm start" -ForegroundColor Gray 
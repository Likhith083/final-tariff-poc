# Start ATLAS Frontend
Write-Host "Starting ATLAS Frontend..." -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "frontend\package.json")) {
    Write-Host "ERROR: Please run this script from the atlas-enterprise directory" -ForegroundColor Red
    exit 1
}

# Change to frontend directory and start
Set-Location frontend
Write-Host "Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

npm run dev 
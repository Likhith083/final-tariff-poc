Write-Host "==============================="
Write-Host "  TariffAI Project Launcher"
Write-Host "==============================="
Write-Host "1. Start backend only"
Write-Host "2. Start frontend only"
Write-Host "3. Start both backend and frontend"
Write-Host "4. Exit"
Write-Host "==============================="

$choice = Read-Host "Enter your choice (1/2/3/4)"

function Start-Backend {
    $backendPath = Join-Path $PSScriptRoot 'backend'
    if (Test-Path $backendPath) {
        $cmd = "cd '$backendPath'; python main.py"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
        Write-Host "[+] Backend started in a new window."
    } else {
        Write-Host "[!] Backend directory not found!"
    }
}

function Start-Frontend {
    $frontendPath = Join-Path $PSScriptRoot 'frontend'
    if (Test-Path $frontendPath) {
        $cmd = "cd '$frontendPath'; npm start"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
        Write-Host "[+] Frontend started in a new window."
    } else {
        Write-Host "[!] Frontend directory not found!"
    }
}

switch ($choice) {
    '1' { Start-Backend }
    '2' { Start-Frontend }
    '3' { Start-Backend; Start-Frontend }
    '4' { Write-Host "Exiting..."; exit }
    default { Write-Host "Invalid choice. Please run the script again and select 1, 2, 3, or 4." }
} 
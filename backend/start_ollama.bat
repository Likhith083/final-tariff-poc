@echo off
echo Starting Ollama for TariffAI...
echo.

REM Check if Ollama is installed
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Ollama is not installed or not in PATH
    echo Please install Ollama from: https://ollama.ai/download
    pause
    exit /b 1
)

echo Checking if Ollama service is running...
curl -s http://localhost:11434/api/version >nul 2>nul
if %errorlevel% neq 0 (
    echo Starting Ollama service...
    start /B ollama serve
    echo Waiting for Ollama to start...
    timeout /t 5 /nobreak >nul
)

echo Checking if llama3.2:3b model is available...
ollama list | findstr "llama3.2:3b" >nul 2>nul
if %errorlevel% neq 0 (
    echo Model llama3.2:3b not found. Downloading...
    echo This may take a few minutes depending on your internet connection...
    ollama pull llama3.2:3b
    if %errorlevel% neq 0 (
        echo ERROR: Failed to download model
        pause
        exit /b 1
    )
) else (
    echo Model llama3.2:3b is already available
)

echo.
echo Testing model...
echo Hello from TariffAI | ollama run llama3.2:3b
if %errorlevel% neq 0 (
    echo ERROR: Model test failed
    pause
    exit /b 1
)

echo.
echo ✅ Ollama is ready for TariffAI!
echo Model: llama3.2:3b
echo Service: http://localhost:11434
echo.
echo You can now use the AI chat feature in TariffAI
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
pause

# ATLAS Enterprise GitHub Repository Setup Script
# This script helps you initialize and push your project to GitHub

Write-Host "🚀 ATLAS Enterprise GitHub Repository Setup" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Check if git is installed
try {
    git --version | Out-Null
    Write-Host "✅ Git is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not installed. Please install Git first." -ForegroundColor Red
    Write-Host "Download from: https://git-scm.com/" -ForegroundColor Yellow
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ Please run this script from the atlas-enterprise directory" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Setting up GitHub repository..." -ForegroundColor Yellow

# Initialize git repository (if not already done)
if (-not (Test-Path ".git")) {
    Write-Host "Initializing git repository..." -ForegroundColor Yellow
    git init
} else {
    Write-Host "✅ Git repository already initialized" -ForegroundColor Green
}

# Add all files
Write-Host "Adding files to git..." -ForegroundColor Yellow
git add .

# Create initial commit
Write-Host "Creating initial commit..." -ForegroundColor Yellow
git commit -m "feat: initial commit - ATLAS Enterprise v2.0.0

- AI-powered trade compliance platform
- Local LLM integration with Ollama
- HTS code management with 12,900+ codes
- Comprehensive tariff calculations
- Multi-persona dashboard
- Docker containerization
- PowerShell deployment scripts"

Write-Host "✅ Initial commit created" -ForegroundColor Green

# Ask for GitHub repository URL
Write-Host ""
Write-Host "🔗 GitHub Repository Setup" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "1. Go to https://github.com/new" -ForegroundColor Yellow
Write-Host "2. Create a new repository named 'atlas-enterprise'" -ForegroundColor Yellow
Write-Host "3. Copy the repository URL (it will look like: https://github.com/yourusername/atlas-enterprise.git)" -ForegroundColor Yellow
Write-Host ""

$repoUrl = Read-Host "Enter your GitHub repository URL"

if ($repoUrl -eq "") {
    Write-Host "❌ No repository URL provided. Setup cancelled." -ForegroundColor Red
    exit 1
}

# Add remote origin
Write-Host "Adding remote origin..." -ForegroundColor Yellow
git remote add origin $repoUrl

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin main

Write-Host ""
Write-Host "🎉 Repository setup complete!" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host ""
Write-Host "Your ATLAS Enterprise repository is now available at:" -ForegroundColor Yellow
Write-Host $repoUrl -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Update the repository URL in README.md" -ForegroundColor Yellow
Write-Host "2. Set up GitHub Actions (optional)" -ForegroundColor Yellow
Write-Host "3. Configure branch protection rules" -ForegroundColor Yellow
Write-Host "4. Add collaborators if needed" -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 Your ATLAS Enterprise project is now ready for collaboration!" -ForegroundColor Green 
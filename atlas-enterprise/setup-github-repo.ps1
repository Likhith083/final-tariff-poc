# ATLAS - GitHub Repository Setup Script
# This script helps you initialize and push your project to GitHub

Write-Host "🚀 ATLAS - GitHub Repository Setup" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Check if git is installed
try {
    git --version | Out-Null
    Write-Host "✅ Git is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not installed. Please install Git first." -ForegroundColor Red
    Write-Host "Download from: https://git-scm.com/downloads" -ForegroundColor Yellow
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ Please run this script from the atlas-enterprise directory" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Current directory is correct" -ForegroundColor Green

# Initialize git repository (if not already done)
if (-not (Test-Path ".git")) {
    Write-Host "📁 Initializing git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "✅ Git repository already exists" -ForegroundColor Green
}

# Add all files
Write-Host "📝 Adding files to git..." -ForegroundColor Yellow
git add .

# Create initial commit
Write-Host "💾 Creating initial commit..." -ForegroundColor Yellow
git commit -m "Initial commit: ATLAS v2.0.0

- AI-powered trade compliance platform
- Local Ollama integration with knowledge base
- Real HTS database with 12,900+ codes
- Multi-country sourcing analysis
- Docker containerization
- Comprehensive API documentation"

Write-Host "✅ Initial commit created" -ForegroundColor Green

# Ask user for GitHub repository URL
Write-Host ""
Write-Host "🔗 GitHub Repository Setup" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To create a GitHub repository:" -ForegroundColor White
Write-Host "1. Go to https://github.com/new" -ForegroundColor White
Write-Host "2. Name your repository (e.g., 'atlas')" -ForegroundColor White
Write-Host "3. Make it public or private" -ForegroundColor White
Write-Host "4. Don't initialize with README (we already have one)" -ForegroundColor White
Write-Host "5. Copy the repository URL" -ForegroundColor White
Write-Host ""

$repoUrl = Read-Host "Enter your GitHub repository URL (e.g., https://github.com/username/atlas)"

if ($repoUrl -eq "") {
    Write-Host "❌ Repository URL is required" -ForegroundColor Red
    exit 1
}

# Add remote origin
Write-Host "🔗 Adding remote origin..." -ForegroundColor Yellow
git remote add origin $repoUrl

# Push to GitHub
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Yellow
git branch -M main
git push -u origin main

Write-Host ""
Write-Host "🎉 Success! Your ATLAS repository is now on GitHub!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Visit your repository: $repoUrl" -ForegroundColor White
Write-Host "2. Set up GitHub Actions (optional)" -ForegroundColor White
Write-Host "3. Configure branch protection rules" -ForegroundColor White
Write-Host "4. Add collaborators if needed" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Development Workflow:" -ForegroundColor Cyan
Write-Host "1. Create feature branches: git checkout -b feature/new-feature" -ForegroundColor White
Write-Host "2. Make changes and commit: git commit -m 'feat: add new feature'" -ForegroundColor White
Write-Host "3. Push and create PR: git push origin feature/new-feature" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "- README.md: Project overview and setup" -ForegroundColor White
Write-Host "- CONTRIBUTING.md: How to contribute" -ForegroundColor White
Write-Host "- CHANGELOG.md: Version history" -ForegroundColor White
Write-Host "- API docs: http://localhost:8000/docs (when running)" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Happy coding!" -ForegroundColor Green 
# GitHub Repository Setup Guide

This guide will help you create a professional GitHub repository for ATLAS Enterprise.

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

1. **Run the setup script**:
   ```powershell
   cd atlas-enterprise
   .\setup-github-repo.ps1
   ```

2. **Follow the prompts** to create your GitHub repository

### Option 2: Manual Setup

1. **Create GitHub Repository**:
   - Go to https://github.com/new
   - Name: `atlas-enterprise`
   - Description: `AI-Powered Trade Compliance Platform`
   - Make it Public or Private
   - **Don't** initialize with README (we already have one)

2. **Initialize Git**:
   ```powershell
   cd atlas-enterprise
   git init
   git add .
   git commit -m "Initial commit: ATLAS Enterprise v2.0.0"
   ```

3. **Connect to GitHub**:
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/atlas-enterprise.git
   git branch -M main
   git push -u origin main
   ```

## 📁 Repository Structure

Your repository will include:

```
atlas-enterprise/
├── .github/                    # GitHub configuration
│   ├── workflows/              # CI/CD pipelines
│   └── ISSUE_TEMPLATE/         # Issue templates
├── backend/                    # FastAPI backend
│   ├── main_unified.py         # Main application
│   ├── agents/                 # AI agents
│   ├── data/                   # HTS database
│   └── Dockerfile              # Backend container
├── frontend/                   # React frontend
│   ├── src/                    # Source code
│   ├── public/                 # Static assets
│   └── Dockerfile              # Frontend container
├── docs/                       # Documentation
├── scripts/                    # Utility scripts
├── docker-compose.yml          # Container orchestration
├── README.md                   # Project overview
├── CONTRIBUTING.md             # Contribution guidelines
├── CHANGELOG.md                # Version history
├── LICENSE                     # MIT license
└── .gitignore                 # Git ignore rules
```

## 🔧 Repository Configuration

### 1. Repository Settings

After creating your repository, configure these settings:

- **Description**: `AI-Powered Trade Compliance Platform with Local Ollama Integration`
- **Topics**: `ai`, `trade-compliance`, `tariff-management`, `ollama`, `fastapi`, `react`
- **Website**: `http://localhost:3000` (for local development)

### 2. Branch Protection

Enable branch protection for `main`:

1. Go to Settings → Branches
2. Add rule for `main` branch
3. Enable:
   - ✅ Require pull request reviews
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date
   - ✅ Include administrators

### 3. GitHub Actions

The repository includes CI/CD workflows:

- **Backend Tests**: Python linting, testing, coverage
- **Frontend Tests**: ESLint, Jest, build verification
- **Docker Build**: Container build and health checks
- **Security Scan**: Trivy vulnerability scanning

### 4. Issue Templates

Three issue templates are included:

- **🐛 Bug Report**: For reporting issues
- **✨ Feature Request**: For suggesting new features
- **❓ Question**: For asking questions

## 📋 Repository Features

### ✅ Professional Documentation

- **README.md**: Comprehensive project overview
- **CONTRIBUTING.md**: Detailed contribution guidelines
- **CHANGELOG.md**: Version history tracking
- **LICENSE**: MIT license for open source

### ✅ Development Tools

- **GitHub Actions**: Automated CI/CD pipeline
- **Issue Templates**: Structured issue reporting
- **Code Quality**: Linting and testing automation
- **Security Scanning**: Vulnerability detection

### ✅ Project Structure

- **Docker Support**: Complete containerization
- **Multi-Environment**: Development and production configs
- **API Documentation**: Auto-generated Swagger docs
- **Type Safety**: TypeScript frontend, Python type hints

## 🎯 Best Practices

### 1. Commit Messages

Use conventional commit messages:

```bash
feat: add new tariff calculation feature
fix: resolve AI chatbot connection issue
docs: update README with setup instructions
style: format code with prettier
refactor: improve HTS search performance
test: add unit tests for tariff calculator
chore: update dependencies
```

### 2. Branch Strategy

- **main**: Production-ready code
- **develop**: Integration branch
- **feature/***: New features
- **fix/***: Bug fixes
- **docs/***: Documentation updates

### 3. Pull Requests

- Use descriptive titles
- Include detailed descriptions
- Add screenshots for UI changes
- Link related issues
- Request reviews from team members

### 4. Issue Management

- Use appropriate labels
- Assign issues to team members
- Set milestones for releases
- Close issues with commit messages

## 🔗 Useful Links

### Repository URLs

- **Repository**: `https://github.com/YOUR_USERNAME/atlas-enterprise`
- **Issues**: `https://github.com/YOUR_USERNAME/atlas-enterprise/issues`
- **Actions**: `https://github.com/YOUR_USERNAME/atlas-enterprise/actions`
- **Releases**: `https://github.com/YOUR_USERNAME/atlas-enterprise/releases`

### Development URLs

- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

## 🚀 Deployment Options

### 1. Local Development

```powershell
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 2. Cloud Deployment

Consider these platforms for production deployment:

- **Railway**: Easy Docker deployment
- **Render**: Free tier with Docker support
- **DigitalOcean**: App Platform with Docker
- **AWS**: ECS or EKS for container orchestration
- **Google Cloud**: Cloud Run for serverless containers

### 3. Environment Variables

Create `.env` files for different environments:

```env
# Development
DATABASE_URL=postgresql+asyncpg://atlas:atlas@postgres:5432/atlas_db
REDIS_URL=redis://redis:6379/0
OLLAMA_BASE_URL=http://localhost:11434

# Production
DATABASE_URL=your-production-db-url
REDIS_URL=your-production-redis-url
OLLAMA_BASE_URL=your-ollama-instance-url
```

## 📈 Repository Analytics

After setup, you can track:

- **Traffic**: Views, clones, downloads
- **Contributors**: Team member activity
- **Issues**: Open/closed, response times
- **Pull Requests**: Merge rates, review times
- **Actions**: Build success rates

## 🎉 Next Steps

1. **Customize**: Update README with your specific details
2. **Configure**: Set up branch protection and team access
3. **Deploy**: Choose a deployment platform
4. **Monitor**: Set up analytics and monitoring
5. **Contribute**: Start developing new features!

---

**Happy coding! 🚀**

Your ATLAS Enterprise repository is now ready for professional development and collaboration. 
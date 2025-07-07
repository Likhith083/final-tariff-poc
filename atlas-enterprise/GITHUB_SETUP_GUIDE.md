# ATLAS Enterprise - GitHub Branch Setup Guide

## Step 1: Initialize Git Repository (if not already done)

```bash
cd "C:\Users\likhi\ATLAS\atlas-enterprise"
git init
```

## Step 2: Create .gitignore file

```bash
# Create .gitignore to exclude unnecessary files
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# Temporary files
tmp/
temp/
*.tmp

# API keys and secrets (keep these secure!)
.env.local
.env.production
secrets.txt

# ChromaDB data
data/chroma/

# Uploads
uploads/
*.xlsx.backup
EOF
```

## Step 3: Add all files to Git

```bash
git add .
```

## Step 4: Create initial commit

```bash
git commit -m "Initial commit: ATLAS Enterprise with real data implementation

- Real Groq API integration for AI responses
- Real exchange rate service using forex-python
- Real tariff lookup from USITC and local database
- Comprehensive API with HTS search, currency conversion, and tariff calculations
- Production-ready services replacing all mock data
- Complete test suite for real data verification"
```

## Step 5: Create and switch to atlas-enterprise branch

```bash
git checkout -b atlas-enterprise
```

## Step 6: Set up GitHub repository (if not already done)

### Option A: If you don't have a GitHub repository yet
1. Go to GitHub.com
2. Click "New repository"
3. Name it "ATLAS" or "atlas-enterprise"
4. Don't initialize with README (since we already have files)
5. Create repository

### Option B: If you already have a repository
Skip to Step 7

## Step 7: Add GitHub remote

```bash
# Replace 'yourusername' with your actual GitHub username
git remote add origin https://github.com/yourusername/ATLAS.git
```

## Step 8: Push the atlas-enterprise branch to GitHub

```bash
git push -u origin atlas-enterprise
```

## Step 9: Verify the branch on GitHub

1. Go to your GitHub repository
2. Click on the branch dropdown (usually shows "main" by default)
3. Select "atlas-enterprise"
4. Verify all your files are there

## Alternative: Using GitHub CLI (if you have it installed)

```bash
# If you have GitHub CLI installed
gh repo create ATLAS --public
git remote add origin https://github.com/Likhith083/ATLAS.git
git push -u origin atlas-enterprise
```

## Project Structure That Will Be Saved:

```
atlas-enterprise/
├── .env                           # Environment configuration
├── .gitignore                     # Git ignore file
├── README.md                      # Project documentation
├── simple_api.py                  # Real data API server
├── simple_test.py                 # Basic system tests
├── test_real_data.py              # Comprehensive real data tests
├── quick_test.py                  # Quick service verification
├── backend/                       # Backend services
│   ├── core/                      # Core configuration
│   │   └── config.py             # Settings management
│   ├── services/                  # Real data services
│   │   ├── groq_service.py       # Real Groq API integration
│   │   ├── exchange_rate_service.py  # Real forex data
│   │   ├── real_tariff_service.py    # Real tariff lookup
│   │   └── tariff_calculation_engine.py  # Production calculations
│   ├── models/                    # Data models
│   ├── schemas/                   # API schemas
│   └── data/                      # Local data files
│       ├── tariff_database_2025.xlsx
│       ├── adcvd_faq.json
│       ├── additional_knowledge.json
│       ├── srs_examples_kb.json
│       └── tariff_management_kb.json
├── frontend/                      # Frontend (if applicable)
└── docs/                         # Documentation
```

## What Makes This Branch Special:

✅ **Real Data Implementation**
- No more mock data
- Live Groq API responses
- Real-time exchange rates
- Actual tariff data from USITC

✅ **Production Ready**
- Error handling
- Caching mechanisms
- Health checks
- Comprehensive logging

✅ **Enterprise Features**
- Multi-currency support
- Alternative country analysis
- HTS code search
- Landed cost calculations

## Next Steps After Pushing:

1. **Create Pull Request**: Create a PR from atlas-enterprise to main
2. **Documentation**: Update README with new features
3. **Testing**: Set up CI/CD for automated testing
4. **Deployment**: Configure production deployment
5. **Monitoring**: Set up application monitoring

## Important Notes:

- Your API keys are in the .env file - keep this secure
- The .gitignore excludes sensitive files
- All services now use real data sources
- Test thoroughly before merging to main branch

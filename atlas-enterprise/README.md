# ATLAS Enterprise - AI-Powered Trade Compliance Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)

> **Enterprise-grade tariff management and trade intelligence platform with AI-powered compliance assistance**

## 🚀 Features

### 🤖 **AI-Powered Trade Intelligence**
- **Local LLM Integration**: Connect with your own Ollama models (llama3.1, llama3.2:3b, qwen3:8b, etc.)
- **Knowledge Base**: Comprehensive trade compliance database with vector search
- **Contextual AI Responses**: Real-time tariff analysis and compliance guidance
- **Multi-Model Support**: Choose from 10+ local models or cloud APIs

### 📊 **HTS Code Management**
- **Real Database**: 12,900+ HTS codes with current duty rates
- **Smart Search**: Fast substring matching with chapter filtering
- **Recent Searches**: Persistent search history with one-click reuse
- **Excel Integration**: Direct import from tariff database files

### 💰 **Tariff Calculations**
- **Comprehensive Cost Analysis**: Duty, MPF, HMF calculations
- **Country-Specific Rates**: Support for Section 301 tariffs and trade agreements
- **Multi-Country Comparison**: Side-by-side sourcing analysis
- **Real-Time Updates**: Current rates and regulatory changes

### 🔍 **Sourcing Optimization**
- **AI Agent Analysis**: Autonomous sourcing recommendations
- **Risk Assessment**: Country-specific risk scoring
- **Cost Comparison**: Total landed cost calculations
- **Trade Agreement Benefits**: GSP, USMCA, FTA analysis

### 👥 **Multi-Persona Dashboard**
- **Procurement Manager**: HTS search, tariff calculation, sourcing analysis
- **Compliance Officer**: Alerts, compliance scoring, regulatory updates
- **Business Analyst**: AI trade intelligence, strategic insights

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React/TS      │    │   FastAPI       │    │   PostgreSQL    │
│   Frontend      │◄──►│   Backend       │◄──►│   Database      │
│   (Port 3000)   │    │   (Port 8000)   │    │   (Port 5432)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐             │
         │              │   Redis         │             │
         │              │   (Port 6379)   │             │
         │              └─────────────────┘             │
         │                       │                       │
         │              ┌─────────────────┐             │
         │              │   Ollama        │             │
         │              │   (Port 11434)  │             │
         │              └─────────────────┘             │
         │                       │                       │
         │              ┌─────────────────┐             │
         │              │   ChromaDB      │             │
         │              │   Vector Store  │             │
         │              └─────────────────┘             │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Docker        │
                    │   Compose       │
                    └─────────────────┘
```

## 🛠️ Technology Stack

### **Frontend**
- **React 18** with TypeScript
- **TanStack Query** for data fetching
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **React Hot Toast** for notifications

### **Backend**
- **FastAPI** with Python 3.11
- **PostgreSQL** for data persistence
- **Redis** for caching and Celery
- **ChromaDB** for vector search
- **Pandas** for Excel data processing

### **AI & ML**
- **Ollama** for local LLM inference
- **LangGraph** for AI agent workflows
- **Vector Search** for knowledge base retrieval
- **Multi-Model Support** (llama3.1, llama3.2:3b, qwen3:8b, etc.)

### **DevOps**
- **Docker Compose** for containerization
- **PowerShell** scripts for Windows deployment
- **Health checks** and monitoring
- **Multi-stage builds** for optimization

## 📦 Installation

### Prerequisites

1. **Docker & Docker Compose**
   ```bash
   # Install Docker Desktop for Windows
   # https://www.docker.com/products/docker-desktop/
   ```

2. **Ollama** (for local AI models)
   ```bash
   # Download from https://ollama.ai/
   # Install and start Ollama
   ollama serve
   ```

3. **Git**
   ```bash
   # Download from https://git-scm.com/
   ```

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/atlas-enterprise.git
   cd atlas-enterprise
   ```

2. **Start the application**
   ```bash
   # Using Docker Compose (recommended)
   docker-compose up -d
   
   # Or using PowerShell scripts
   .\start_atlas_demo.ps1
   ```

3. **Access the application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

### Manual Setup (Development)

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r simple_requirements.txt
   python main_unified.py
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 🎯 Usage

### **AI Chatbot**
1. Navigate to the AI Chatbot page
2. Select your preferred Ollama model
3. Ask questions about:
   - HTS code classification
   - Tariff calculations
   - Trade compliance
   - Sourcing optimization

### **HTS Search**
1. Use the search bar to find HTS codes
2. Filter by chapter or description
3. View duty rates and product details
4. Access recent searches from the sidebar

### **Tariff Calculator**
1. Enter HTS code and product value
2. Specify country of origin
3. Add freight and insurance costs
4. Get comprehensive cost breakdown

### **Sourcing Analysis**
1. Describe your product
2. Select target countries
3. Get AI-powered recommendations
4. Compare costs and risks

## 🔧 Configuration

### **Environment Variables**

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://atlas:atlas@postgres:5432/atlas_db
REDIS_URL=redis://redis:6379/0

# AI Models
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.1

# API Keys (optional)
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key

# Development
DEBUG=true
LOG_LEVEL=INFO
```

### **Ollama Models**

Install your preferred models:

```bash
# Install models
ollama pull llama3.1
ollama pull llama3.2:3b
ollama pull qwen3:8b
ollama pull deepseek-r1:8b

# List available models
ollama list
```

## 📊 Data Sources

### **HTS Database**
- **Source**: Excel file with 12,900+ HTS codes
- **Format**: `backend/data/tariff_database_2025.xlsx`
- **Columns**: hts_code, description, general_rate, FTA columns

### **Knowledge Base**
- **Trade Compliance**: Tariff management best practices
- **SRS Examples**: Specific requirements and standards
- **ADCVD FAQ**: Anti-dumping and countervailing duties
- **Additional Knowledge**: Regulatory updates and guidance

## 🧪 Testing

### **API Testing**
```bash
# Health check
curl http://localhost:8000/health

# HTS search
curl "http://localhost:8000/api/v1/tariff/hts/search?query=laptop"

# AI chat
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"What is the HTS code for laptops?"}],"model":"llama3.1"}'
```

### **Frontend Testing**
```bash
cd frontend
npm test
```

## 🚀 Deployment

### **Production Deployment**

1. **Build production images**
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```

2. **Deploy with environment variables**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Set up reverse proxy (nginx)**
   ```bash
   # Configure nginx for SSL termination
   # Point to localhost:3000 (frontend) and localhost:8000 (backend)
   ```

### **Cloud Deployment**

- **AWS**: Use ECS or EKS with RDS and ElastiCache
- **Azure**: Use AKS with Azure Database and Redis Cache
- **GCP**: Use GKE with Cloud SQL and Memorystore

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### **Development Guidelines**

- Follow **TypeScript** best practices
- Use **Python type hints**
- Write **comprehensive tests**
- Update **documentation**
- Follow **conventional commits**

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama** for local LLM inference
- **FastAPI** for the excellent web framework
- **React** and **TanStack** for the frontend ecosystem
- **ChromaDB** for vector search capabilities
- **Docker** for containerization

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/atlas-enterprise/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/atlas-enterprise/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/atlas-enterprise/wiki)

---

**Made with ❤️ for the global trade community** 
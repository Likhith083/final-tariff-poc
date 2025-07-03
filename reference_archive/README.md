# 🚢 TariffAI - Intelligent HTS & Tariff Management

A comprehensive, AI-powered tariff management system built as a modern monorepo with FastAPI backend, React frontend, ChromaDB vector search, and Ollama LLM integration.

## ✨ Features

### 🎯 Core Capabilities (Phase 1)
- **AI Chatbot with Knowledge Base**: Conversational AI powered by Ollama LLM with ChromaDB for semantic retrieval
- **HTS Code Lookup**: Intelligent search and classification with AI-powered suggestions
- **Modern UI/UX**: Glassmorphism design with Framer Motion animations
- **Real-time Chat**: Streaming responses with markdown and code rendering

### 🚧 Coming Soon (Phase 2)
- **Data Ingestion**: Upload and process Excel/CSV files
- **Tariff Calculation**: Compute tariffs and landed costs
- **Material Analyzer**: Alternative material suggestions
- **Scenario Simulation**: What-if analysis for sourcing decisions

## 🏗️ Architecture

```
tariff-ai/
├── backend/           # FastAPI, ChromaDB, Ollama, SQLite, agents
├── frontend/          # React, Framer Motion, glassmorphism UI
├── database/          # DB init scripts, migrations
├── docs/              # Documentation
├── docker-compose.yml # Unified orchestration
└── README.md
```

### Tech Stack
- **Backend**: FastAPI, ChromaDB, Ollama, SQLite, Pydantic
- **Frontend**: React, Framer Motion, Axios, Lucide Icons
- **AI/ML**: Ollama LLM, ChromaDB Vector Search
- **DevOps**: Docker, Docker Compose

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 16+ (for local development)
- Python 3.8+ (for local development)

### Option 1: Docker (Recommended)
```bash
# Clone the repository
git clone <your-repo-url>
cd tariff-ai

# Copy environment file
cp env.example .env

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development
```bash
# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Frontend Setup (in new terminal)
cd frontend
npm install
npm start
```

## 📊 API Endpoints

### Chat API
- `POST /api/v1/chat/` - Send message to AI assistant
- `GET /api/v1/chat/health` - Chat service health check

### HTS API
- `GET /api/v1/hts/search` - Search HTS codes
- `GET /api/v1/hts/{code}` - Get HTS code details
- `POST /api/v1/hts/classify` - AI-powered classification

### Health & Status
- `GET /health` - Overall system health
- `GET /` - API information and documentation links

## 🎨 UI Features

### Design System
- **Glassmorphism**: Modern glass-like UI elements with backdrop blur
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Smooth Animations**: Framer Motion powered transitions and micro-interactions
- **Dark/Light Theme**: Beautiful gradient backgrounds with excellent contrast

### Interactive Elements
- **Real-time Chat**: Live conversation with AI assistant
- **Smart Suggestions**: Context-aware quick action buttons
- **Loading States**: Elegant loading animations and progress indicators
- **Error Handling**: User-friendly error messages and recovery options

## 🔧 Configuration

### Environment Variables
Copy `env.example` to `.env` and configure:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000

# AI/ML Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Vector Database
CHROMA_DB_PATH=./data/chroma

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚀 Deployment

### Production Build
```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.prod.yml up --build
```

### Local Development
```bash
# Start development environment
docker-compose up --build
```

## 🔍 Usage Examples

### AI Chatbot
```
User: "What is the tariff rate for HTS 8471.30.01?"
AI: "HTS code 8471.30.01 refers to 'Portable automatic data processing machines' 
     with a tariff rate of 0.0% for most countries under normal trade relations."
```

### HTS Lookup
```
User: "Find HTS codes for smartphones"
AI: "I found HTS code 8517.13.00 for 'Smartphones and mobile phones' 
     with a tariff rate of 0.0%."
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FastAPI** for the excellent async web framework
- **React** and **Framer Motion** for the beautiful UI
- **ChromaDB** for vector search capabilities
- **Ollama** for local LLM support

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation at `/docs` when the backend is running
- Review the API documentation at `/redoc`

---

**Built with ❤️ for intelligent tariff management** 
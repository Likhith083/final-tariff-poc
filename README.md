# 🚢 ATLAS - Intelligent HTS & Tariff Management

A comprehensive, AI-powered tariff management system that consolidates the best features from multiple projects into a clean, modern, and scalable solution.

## ✨ Features

### 🎯 Core Capabilities
- **Tariff Impact Calculation**: Compute tariffs and landed costs based on HS/HTS codes and material prices
- **Product Detail Search & HTS Code Inference**: Retrieve product information and assign HTS codes using AI
- **Material Proportion Suggestions**: Recommend alternative material compositions to reduce tariffs
- **What-If Scenario Simulation**: Project cost impacts of tariff rate or sourcing country changes
- **Alternative Sourcing Suggestions**: Propose countries with favorable tariffs
- **Real-time Chat Interface**: Conversational AI for tariff-related queries

### 🏗️ Architecture
- **Agentic AI System**: Specialized agents for classification, calculation, and material analysis
- **FastAPI Backend**: Modern, async Python backend with comprehensive API
- **React Frontend**: Beautiful, responsive UI with glassmorphism design and animations
- **SQLite Database**: Lightweight, reliable data storage
- **ChromaDB Vector Search**: Semantic search for HTS codes and product descriptions
- **Ollama Integration**: Local LLM support for intelligent responses

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Ollama (optional, for local LLM)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend server:**
   ```bash
   python main.py
   ```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

The frontend will be available at `http://localhost:3000`

## 📁 Project Structure

```
tariff-ai-consolidated/
├── backend/
│   ├── app/
│   │   ├── agents/           # AI agents (orchestrator, classification, etc.)
│   │   │   └── v1/          # API endpoints
│   │   ├── api/
│   │   │   └── v1/          # API endpoints
│   │   ├── core/            # Configuration, database, responses
│   │   └── services/        # Business logic services
│   ├── data/               # Data files and ChromaDB storage
│   ├── main.py             # FastAPI application entry point
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   ├── App.js          # Main React app
│   │   └── App.css         # Styles with glassmorphism
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
└── database/              # Database initialization scripts
```

## 🤖 AI Agents

### Orchestrator Agent
- **Purpose**: Master coordinator that routes queries to appropriate specialist agents
- **Capabilities**: Intent analysis, entity extraction, response coordination

### Classification Agent
- **Purpose**: HTS code expert for product classification and search
- **Capabilities**: Vector search, semantic matching, code validation

### Tariff Calculator Agent
- **Purpose**: Cost analysis and calculation specialist
- **Capabilities**: Tariff calculations, scenario simulation, alternative sourcing

### Material Analyzer Agent
- **Purpose**: Material composition and optimization specialist
- **Capabilities**: Material inference, alternative suggestions, quality assessment

## 🎨 UI Features

### Design System
- **Glassmorphism**: Modern glass-like UI elements with backdrop blur
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Smooth Animations**: Framer Motion powered transitions and micro-interactions
- **Dark Theme**: Beautiful gradient backgrounds with excellent contrast

### Interactive Elements
- **Real-time Chat**: Live conversation with AI assistant
- **Smart Suggestions**: Context-aware quick action buttons
- **Loading States**: Elegant loading animations and progress indicators
- **Error Handling**: User-friendly error messages and recovery options

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/tariff_ai.db

# AI/ML
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Vector Database
CHROMA_DB_PATH=./data/chroma

# External APIs (optional)
SERP_API_KEY=your_serp_api_key
CURRENCY_API_KEY=your_currency_api_key

# CORS
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

## 📊 API Endpoints

### Chat API
- `POST /api/v1/chat/` - Send message to AI assistant
- `GET /api/v1/chat/session/{session_id}` - Get session information
- `DELETE /api/v1/chat/session/{session_id}` - Clear session
- `GET /api/v1/chat/health` - Chat service health check

### Health & Status
- `GET /health` - Overall system health
- `GET /` - API information and documentation links

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
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend
cd frontend
npm run build
```

### Docker Deployment (Optional)
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🔍 Usage Examples

### Tariff Calculation
```
User: "Calculate tariff for HTS 8471.30.01 with $500 material cost from China"
AI: "Tariff calculation for HTS 8471.30.01 from China:
     • Material Cost: $500.00
     • Tariff Rate: 25.0%
     • Tariff Amount: $125.00
     • Total Landed Cost: $626.05"
```

### HTS Code Search
```
User: "Find HTS codes for smartphones"
AI: "I found HTS code 8517.13.00 for 'Smartphones and mobile phones' with a tariff rate of 0.0%."
```

### Material Analysis
```
User: "Analyze material composition for nitrile gloves"
AI: "Material analysis for gloves:
     • Nitrile: 100% (tariff: 3.0%)
     Suggested HTS Code: 4015.19.05"
```

### Scenario Simulation
```
User: "Compare sourcing from China vs Mexico for HTS 8471.30.01"
AI: "Scenario comparison:
     Original (from China): $626.05
     New (from Mexico): $501.05
     Difference: -$125.00 (-20.0%)"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** for the excellent async web framework
- **React** and **Framer Motion** for the beautiful UI
- **ChromaDB** for vector search capabilities
- **Ollama** for local LLM support
- **Inter font** for the beautiful typography

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation at `/docs` when the backend is running
- Review the API documentation at `/redoc`

---

**Built with ❤️ for intelligent tariff management** 
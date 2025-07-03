# TariffAI - Fresh Consolidated Edition

## Overview

TariffAI is a modern, intelligent tariff management system that combines the best features from multiple approaches into a clean, maintainable architecture. This fresh implementation provides:

- **FastAPI Backend**: Clean, modular API with proper separation of concerns
- **Modern Frontend**: Vanilla JavaScript with modern CSS for simplicity and performance
- **Agentic Architecture**: Specialized agents for different business scenarios
- **Vector Search**: ChromaDB integration for intelligent HTS code search
- **LLM Integration**: Ollama support for natural language processing
- **Production Ready**: Docker support, proper logging, and error handling

## Architecture

### Backend Structure
```
fresh_tariff_ai/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── chat.py          # Chat endpoints
│   │       ├── hts.py           # HTS search endpoints
│   │       ├── tariff.py        # Tariff calculation endpoints
│   │       └── router.py        # API router
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database connections
│   │   └── responses.py         # Standardized responses
│   ├── agents/
│   │   ├── orchestrator.py      # Main agent coordinator
│   │   ├── classification.py    # HTS classification agent
│   │   ├── calculation.py       # Tariff calculation agent
│   │   └── risk_assessment.py   # Risk assessment agent
│   ├── services/
│   │   ├── ai_service.py        # LLM integration
│   │   ├── search_service.py    # Vector search service
│   │   └── tariff_service.py    # Tariff calculation service
│   └── models/
│       ├── chat.py              # Chat models
│       ├── hts.py               # HTS models
│       └── tariff.py            # Tariff models
├── data/
│   ├── chroma/                  # ChromaDB storage
│   └── tariff_database_2025.xlsx # Tariff data
├── frontend/
│   ├── index.html               # Main interface
│   ├── styles.css               # Modern CSS
│   └── app.js                   # Frontend logic
├── main.py                      # FastAPI application
├── requirements.txt             # Dependencies
└── docker-compose.yml           # Docker setup
```

### Key Features

#### 1. **Agentic Architecture**
- **Orchestrator Agent**: Routes queries to appropriate specialists
- **Classification Agent**: AI-powered HTS code classification
- **Calculation Agent**: Comprehensive tariff calculations
- **Risk Assessment Agent**: Compliance and risk analysis

#### 2. **Intelligent Search**
- **Vector Search**: ChromaDB with sentence transformers
- **Fallback Search**: Direct text search when AI unavailable
- **Real-time Results**: Debounced search with instant feedback

#### 3. **Modern Frontend**
- **Glassmorphism Design**: Beautiful, modern UI
- **Responsive Layout**: Works on all devices
- **Real-time Updates**: Live search and calculations
- **Progressive Enhancement**: Works without JavaScript

#### 4. **Production Features**
- **Docker Support**: Easy deployment
- **Health Checks**: Comprehensive monitoring
- **Error Handling**: Graceful degradation
- **Logging**: Structured logging with different levels

## Quick Start

### Prerequisites
- Python 3.8+
- Ollama (optional, for LLM features)
- Docker (optional)

### Installation

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd fresh_tariff_ai
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Install Ollama (optional)**
   ```bash
   # Download from https://ollama.ai
   ollama pull llama3.2:3b
   ```

3. **Run the application**
   ```bash
   # Development
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Or with Docker
   docker-compose up
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs

## API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `POST /api/v1/chat` - AI chat interface
- `POST /api/v1/hts/search` - HTS code search
- `POST /api/v1/tariff/calculate` - Tariff calculations

### Advanced Endpoints
- `POST /api/v1/scenario/simulate` - Scenario analysis
- `POST /api/v1/sourcing/suggest` - Alternative sourcing
- `POST /api/v1/risk/assess` - Risk assessment
- `POST /api/v1/currency/convert` - Currency conversion

## Technology Stack

### Backend
- **Framework**: FastAPI with async support
- **Database**: ChromaDB for vector storage
- **AI/ML**: Sentence Transformers, Ollama LLM
- **Architecture**: Agentic design with microservices pattern

### Frontend
- **Framework**: Vanilla JavaScript (ES6+)
- **Styling**: Modern CSS with Grid/Flexbox
- **Design**: Glassmorphism with animations
- **Responsive**: Mobile-first approach

### Infrastructure
- **Server**: Uvicorn ASGI server
- **Containerization**: Docker with docker-compose
- **Monitoring**: Health checks and structured logging
- **Security**: CORS, input validation, rate limiting

## Development

### Project Structure Benefits
1. **Modularity**: Each component has a single responsibility
2. **Testability**: Easy to unit test individual components
3. **Maintainability**: Clear separation of concerns
4. **Scalability**: Easy to add new features or agents
5. **Performance**: Optimized for speed and efficiency

### Adding New Features
1. **Backend**: Add new agents in `app/agents/` or endpoints in `app/api/v1/`
2. **Frontend**: Update `frontend/app.js` and `frontend/styles.css`
3. **Models**: Define new Pydantic models in `app/models/`
4. **Services**: Add business logic in `app/services/`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

---

**TariffAI** - Making international trade smarter and more efficient with a fresh, modern approach. 
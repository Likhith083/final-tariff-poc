# TariffAI Backend

Enterprise-grade tariff management chatbot with AI-powered insights.

## Features

- **HTS Code Search**: Accurate HTS code lookup and classification
- **Tariff Calculations**: Real-time tariff and landed cost calculations
- **Scenario Analysis**: What-if scenario simulation for cost optimization
- **Risk Assessment**: AI-powered risk analysis and compliance checking
- **Analytics**: Comprehensive reporting and data visualization
- **Chat Interface**: Conversational AI for natural language queries

## Project Structure

```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Core configuration and database
│   ├── services/        # Business logic services
│   ├── agents/          # AI agents and orchestrators
│   └── db/              # Database models, schemas, and CRUD
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container configuration
└── docker-compose.yml   # Service orchestration
```

## Quick Start

### Prerequisites

- Python 3.8+
- SQLite (or PostgreSQL for production)
- Ollama (for local LLM)

### Installation

1. **Clone and navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application:**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Core Endpoints

- `GET /` - Application info
- `GET /health` - Health check
- `GET /api/v1/status` - API status

### HTS Search

- `POST /api/v1/hts/search` - Search HTS codes
- `GET /api/v1/hts/codes/{hts_code}` - Get HTS code details

### Tariff Calculations

- `POST /api/v1/tariff/calculate` - Calculate tariffs
- `POST /api/v1/tariff/landed-cost` - Calculate landed costs

### Scenario Analysis

- `POST /api/v1/scenario/create` - Create scenario
- `GET /api/v1/scenario/list` - List scenarios
- `POST /api/v1/scenario/analyze` - Analyze scenario

### Risk Assessment

- `POST /api/v1/risk/assess` - Assess risks
- `GET /api/v1/risk/reports` - Get risk reports

### Analytics

- `GET /api/v1/analytics/dashboard` - Dashboard data
- `POST /api/v1/analytics/reports` - Generate reports

### Chat

- `POST /api/v1/chat/message` - Send chat message
- `GET /api/v1/chat/history` - Get chat history

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

### Type Checking

```bash
mypy .
```

## Docker

### Build and Run

```bash
docker build -t tariff-ai-backend .
docker run -p 8000:8000 tariff-ai-backend
```

### Using Docker Compose

```bash
docker-compose up --build
```

## Configuration

Key environment variables:

- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - Application secret key
- `OLLAMA_BASE_URL` - Ollama server URL
- `OLLAMA_MODEL` - LLM model name
- `CHROMA_DB_PATH` - ChromaDB storage path

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License 
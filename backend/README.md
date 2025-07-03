# Tariff AI Backend

A FastAPI-based backend for the Tariff AI system, providing AI-powered tariff management, HTS code lookup, and duty calculations.

## Features

- **AI Chat Interface**: Intelligent conversations about trade and tariffs
- **HTS Code Lookup**: Search and classify Harmonized Tariff Schedule codes
- **Tariff Calculator**: Calculate duties and fees for imports
- **User Authentication**: JWT-based authentication system
- **Database Integration**: SQLAlchemy with SQLite (easily switchable to PostgreSQL)
- **AI Integration**: Ollama LLM for intelligent responses
- **RESTful API**: Clean, documented API endpoints

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLAlchemy + SQLite
- **Authentication**: JWT with Passlib
- **AI/LLM**: Ollama integration
- **Documentation**: Auto-generated with FastAPI
- **Validation**: Pydantic models

## Quick Start

### Prerequisites

1. Python 3.8+
2. Ollama installed and running locally
3. pip or poetry for dependency management

### Installation

1. **Clone and navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token
- `GET /api/v1/auth/me` - Get current user info

### Chat
- `POST /api/v1/chat/send` - Send message to AI
- `GET /api/v1/chat/sessions` - Get chat sessions
- `GET /api/v1/chat/sessions/{id}/messages` - Get session messages
- `DELETE /api/v1/chat/sessions/{id}` - Delete session
- `WS /api/v1/chat/ws/{user_id}` - WebSocket for real-time chat

### HTS Lookup
- `GET /api/v1/hts/search` - Search HTS codes
- `GET /api/v1/hts/code/{code}` - Get specific HTS code
- `GET /api/v1/hts/suggestions` - Get autocomplete suggestions
- `GET /api/v1/hts/categories` - Get all categories
- `GET /api/v1/hts/category/{category}` - Get codes by category
- `POST /api/v1/hts/import` - Import HTS data (admin only)
- `GET /api/v1/hts/stats` - Get database statistics

### Calculator
- `POST /api/v1/calculator/calculate` - Calculate duty
- `GET /api/v1/calculator/history` - Get calculation history
- `GET /api/v1/calculator/history/{id}` - Get specific calculation
- `DELETE /api/v1/calculator/history/{id}` - Delete calculation
- `POST /api/v1/calculator/batch` - Batch calculations
- `GET /api/v1/calculator/summary` - Get calculation summary

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── chat.py          # Chat endpoints
│   │       ├── hts.py           # HTS lookup endpoints
│   │       └── calculator.py    # Calculator endpoints
│   ├── core/
│   │   ├── config.py            # Configuration settings
│   │   └── database.py          # Database setup
│   ├── models/
│   │   ├── user.py              # User model
│   │   ├── chat.py              # Chat models
│   │   ├── hts.py               # HTS model
│   │   └── tariff.py            # Tariff calculation model
│   ├── schemas/
│   │   ├── auth.py              # Auth request/response models
│   │   ├── chat.py              # Chat request/response models
│   │   ├── hts.py               # HTS request/response models
│   │   └── tariff.py            # Tariff request/response models
│   └── services/
│       ├── ai_service.py        # AI/LLM integration
│       ├── hts_service.py       # HTS data management
│       └── calculator_service.py # Duty calculations
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Configuration

Key configuration options in `.env`:

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT secret key
- `OLLAMA_BASE_URL`: Ollama server URL
- `OLLAMA_MODEL`: LLM model to use
- `DEBUG`: Enable debug mode

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
```bash
alembic upgrade head
```

### Code Formatting
```bash
black .
isort .
```

## Deployment

### Production Setup
1. Use PostgreSQL instead of SQLite
2. Set `DEBUG=false`
3. Use strong `SECRET_KEY`
4. Configure proper CORS origins
5. Set up logging
6. Use production WSGI server (Gunicorn)

### Docker Deployment
```bash
docker build -t tariff-ai-backend .
docker run -p 8000:8000 tariff-ai-backend
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License. 
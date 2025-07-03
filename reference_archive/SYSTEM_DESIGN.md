# SYSTEM DESIGN DOCUMENT
# TARIFF MANAGEMENT CHATBOT

## 1. SYSTEM OVERVIEW

### 1.1 Architecture Pattern
The Tariff Management Chatbot follows a **Microservices Architecture** with **Event-Driven Design** for real-time processing and **Layered Architecture** for separation of concerns.

### 1.2 High-Level System Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│  Web Interface (React/HTML)  │  Mobile Interface  │  API Gateway │
└─────────────────────────────┼─────────────────────┼──────────────┘
                              │                     │
                              ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  Chat Service  │  Tariff Service  │  Search Service  │  Report   │
│                │                  │                  │  Service  │
└────────────────┼──────────────────┼──────────────────┼───────────┘
                 │                  │                  │
                 ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DOMAIN LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  Business Logic  │  AI/ML Engine  │  Calculation Engine  │      │
│                  │                │                      │      │
└──────────────────┼────────────────┼──────────────────────┼──────┘
                   │                │                      │
                   ▼                ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  Vector DB  │  SQLite  │  File Storage  │  External APIs  │     │
│  (ChromaDB) │          │                │                 │     │
└─────────────┼──────────┼────────────────┼─────────────────┼─────┘
              │          │                │                 │
              ▼          ▼                ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  Docker  │  Uvicorn  │  Nginx  │  Monitoring  │  Logging  │     │
└──────────┴───────────┴─────────┴──────────────┴───────────┴─────┘
```

## 2. COMPONENT DESIGN

### 2.1 Frontend Components
```javascript
// Component Hierarchy
App
├── ChatInterface
│   ├── MessageList
│   ├── InputForm
│   └── StatusIndicator
├── TabNavigation
│   ├── AIChat
│   ├── DataIngestion
│   ├── HTSSearch
│   ├── CurrencyConverter
│   ├── TariffLookup
│   └── ScenarioSimulation
└── SystemStatus
    ├── BackendStatus
    ├── LLMStatus
    └── DatabaseStatus
```

### 2.2 Backend Services Architecture
```python
# Service Layer Structure
services/
├── chat_service.py          # Conversational AI logic
├── tariff_service.py        # Tariff calculations
├── search_service.py        # HTS code search
├── serp_service.py          # Product detail extraction
├── material_service.py      # Material composition analysis
├── scenario_service.py      # What-if simulations
├── reporting_service.py     # Report generation
├── alert_service.py         # Notification system
└── external_api_service.py  # External API integrations
```

### 2.3 Data Models
```python
# Core Data Models
class Product:
    id: str
    name: str
    description: str
    company: str
    material_composition: Dict[str, float]
    hts_codes: List[str]
    tariff_rates: Dict[str, float]

class TariffCalculation:
    hts_code: str
    country_origin: str
    value: float
    tariff_rate: float
    tariff_amount: float
    landed_cost: float
    effective_date: datetime

class MaterialSuggestion:
    original_composition: Dict[str, float]
    suggested_composition: Dict[str, float]
    cost_savings: float
    quality_impact: float
    justification: str

class Scenario:
    base_scenario: TariffCalculation
    modified_scenario: TariffCalculation
    savings: float
    risk_assessment: str
```

## 3. DATA FLOW DESIGN

### 3.1 Product Search and Classification Flow
```
User Input: "McKesson nitrile gloves"
    │
    ▼
1. SERP API Query
    │
    ▼
2. Product Detail Extraction
    │
    ▼
3. Material Composition Inference
    │
    ▼
4. HTS Code Classification
    │
    ▼
5. Tariff Rate Lookup
    │
    ▼
6. Cost Calculation
    │
    ▼
7. Response Generation
```

### 3.2 Material Optimization Flow
```
Current Material: "100% cotton"
    │
    ▼
1. Analyze Current Tariff Impact
    │
    ▼
2. Identify High-Tariff Materials
    │
    ▼
3. Search Alternative Materials
    │
    ▼
4. Calculate Quality Impact
    │
    ▼
5. Rank Alternatives by Savings
    │
    ▼
6. Generate Recommendations
```

### 3.3 Scenario Simulation Flow
```
Base Scenario: China, 5% tariff
    │
    ▼
1. Calculate Base Costs
    │
    ▼
2. Apply Scenario Changes
    │
    ▼
3. Recalculate Tariffs
    │
    ▼
4. Compare Results
    │
    ▼
5. Generate Insights
```

## 4. DATABASE DESIGN

### 4.1 Vector Database Schema (ChromaDB)
```python
# Collection: hts_search
{
    "id": "unique_id",
    "hts_code": "4015.19.0510",
    "description": "Nitrile gloves, disposable",
    "embedding": [0.1, 0.2, 0.3, ...],  # 1536-dimensional vector
    "metadata": {
        "tariff_rate": 3.0,
        "country": "US",
        "effective_date": "2025-01-01",
        "material_type": "rubber",
        "product_category": "medical_supplies"
    }
}
```

### 4.2 Relational Database Schema (SQLite)
```sql
-- Products table
CREATE TABLE products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    company TEXT,
    material_composition JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tariff rates table
CREATE TABLE tariff_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hts_code TEXT NOT NULL,
    country TEXT NOT NULL,
    rate DECIMAL(5,2) NOT NULL,
    effective_date DATE NOT NULL,
    trade_program TEXT,
    UNIQUE(hts_code, country, effective_date)
);

-- User sessions table
CREATE TABLE user_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    session_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Alerts table
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    hts_code TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    threshold DECIMAL(10,2),
    email TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.3 File Storage Structure
```
data/
├── tariff_database_2025.xlsx    # Main tariff data
├── material_properties.json     # Material characteristics
├── company_database.json        # Company information
├── trade_agreements.json        # FTA data
└── uploads/                     # User uploaded files
    ├── product_catalogs/
    ├── material_specs/
    └── reports/
```

## 5. API DESIGN

### 5.1 RESTful API Endpoints
```python
# Core API Endpoints
POST   /api/chat                    # Conversational interface
POST   /api/hts/search              # HTS code search
POST   /api/tariff/calculate        # Tariff calculations
POST   /api/product/analyze         # Product analysis
POST   /api/material/suggest        # Material suggestions
POST   /api/scenario/simulate       # Scenario simulation
POST   /api/sourcing/suggest        # Alternative sourcing
POST   /api/currency/convert        # Currency conversion
GET    /api/reports/generate        # Report generation
POST   /api/alerts/subscribe        # Alert subscription
GET    /api/health                  # System health check
```

### 5.2 WebSocket Events
```javascript
// Real-time communication
{
    "event": "chat_message",
    "data": {
        "message": "What's the tariff for cotton shirts?",
        "timestamp": "2025-06-29T19:00:00Z"
    }
}

{
    "event": "search_progress",
    "data": {
        "progress": 75,
        "status": "Analyzing product details..."
    }
}

{
    "event": "calculation_complete",
    "data": {
        "result": {
            "tariff_amount": 0.70,
            "landed_cost": 11.00
        }
    }
}
```

## 6. INTEGRATION DESIGN

### 6.1 External API Integrations
```python
# API Integration Layer
class ExternalAPIService:
    def __init__(self):
        self.serp_api = SERPAPIClient()
        self.tariff_api = TariffAPIClient()
        self.currency_api = CurrencyAPIClient()
        self.llm_api = OllamaClient()
    
    async def get_product_details(self, query: str) -> ProductDetails:
        """Extract product information from SERP APIs"""
        pass
    
    async def get_tariff_rate(self, hts_code: str, country: str) -> float:
        """Retrieve tariff rates from USITC/WTO"""
        pass
    
    async def convert_currency(self, amount: float, from_curr: str, to_curr: str) -> float:
        """Convert currencies using forex-python"""
        pass
    
    async def enhance_query(self, query: str) -> str:
        """Enhance search queries using LLM"""
        pass
```

### 6.2 Data Source Integration
```python
# Data Source Management
class DataSourceManager:
    def __init__(self):
        self.sources = {
            'usitc': USITCDataSource(),
            'wto': WTODataSource(),
            'un_comtrade': UNComtradeDataSource(),
            'wco': WCODataSource(),
            'avalara': AvalaraDataSource()
        }
    
    async def get_tariff_data(self, hts_code: str, country: str) -> TariffData:
        """Aggregate tariff data from multiple sources"""
        pass
    
    async def validate_hts_code(self, hts_code: str) -> bool:
        """Validate HTS code against official sources"""
        pass
    
    async def get_material_data(self, material: str) -> MaterialData:
        """Get material properties and trade data"""
        pass
```

## 7. AI/ML COMPONENTS

### 7.1 LLM Integration Architecture
```python
# LLM Service Design
class LLMService:
    def __init__(self, model_name: str = "llama3.2:3b"):
        self.model = model_name
        self.client = OllamaClient()
        self.prompts = PromptTemplates()
    
    async def enhance_search_query(self, query: str) -> str:
        """Enhance user queries for better semantic search"""
        prompt = self.prompts.get_enhancement_prompt(query)
        return await self.client.generate(prompt)
    
    async def classify_product(self, description: str) -> List[str]:
        """Classify products and suggest HTS codes"""
        prompt = self.prompts.get_classification_prompt(description)
        response = await self.client.generate(prompt)
        return self.parse_hts_codes(response)
    
    async def suggest_materials(self, current_materials: Dict[str, float]) -> List[MaterialSuggestion]:
        """Suggest alternative material compositions"""
        prompt = self.prompts.get_material_suggestion_prompt(current_materials)
        response = await self.client.generate(prompt)
        return self.parse_material_suggestions(response)
```

### 7.2 Vector Search Implementation
```python
# Vector Search Service
class VectorSearchService:
    def __init__(self, collection_name: str = "hts_search"):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(collection_name)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    async def search_hts_codes(self, query: str, limit: int = 10) -> List[HTSSearchResult]:
        """Search HTS codes using semantic similarity"""
        # Generate embedding for query
        query_embedding = self.embedding_model.encode(query)
        
        # Search in vector database
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=limit,
            include=['metadatas', 'distances']
        )
        
        return self.format_results(results)
    
    async def add_hts_code(self, hts_code: str, description: str, metadata: dict):
        """Add new HTS code to vector database"""
        embedding = self.embedding_model.encode(description)
        self.collection.add(
            embeddings=[embedding.tolist()],
            documents=[description],
            metadatas=[metadata],
            ids=[hts_code]
        )
```

## 8. SECURITY DESIGN

### 8.1 Authentication & Authorization
```python
# Security Middleware
class SecurityMiddleware:
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.api_key_validator = APIKeyValidator()
    
    async def authenticate_request(self, request: Request) -> bool:
        """Validate API keys and rate limits"""
        # Check API key
        api_key = request.headers.get('X-API-Key')
        if not self.api_key_validator.validate(api_key):
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Check rate limit
        client_id = request.client.host
        if not self.rate_limiter.check_limit(client_id):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        return True
```

### 8.2 Data Protection
```python
# Data Encryption
class DataProtection:
    def __init__(self):
        self.encryption_key = os.getenv('ENCRYPTION_KEY')
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive tariff and user data"""
        pass
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data for processing"""
        pass
```

## 9. PERFORMANCE OPTIMIZATION

### 9.1 Caching Strategy
```python
# Caching Layer
class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis()
        self.cache_ttl = {
            'tariff_rates': 3600,      # 1 hour
            'currency_rates': 300,     # 5 minutes
            'hts_search': 1800,        # 30 minutes
            'product_details': 7200    # 2 hours
        }
    
    async def get_cached_tariff_rate(self, hts_code: str, country: str) -> Optional[float]:
        """Get cached tariff rate"""
        cache_key = f"tariff:{hts_code}:{country}"
        return self.redis_client.get(cache_key)
    
    async def cache_tariff_rate(self, hts_code: str, country: str, rate: float):
        """Cache tariff rate"""
        cache_key = f"tariff:{hts_code}:{country}"
        self.redis_client.setex(cache_key, self.cache_ttl['tariff_rates'], rate)
```

### 9.2 Database Optimization
```sql
-- Indexes for performance
CREATE INDEX idx_hts_code ON tariff_rates(hts_code);
CREATE INDEX idx_country ON tariff_rates(country);
CREATE INDEX idx_effective_date ON tariff_rates(effective_date);
CREATE INDEX idx_user_alerts ON alerts(user_id, hts_code);
CREATE INDEX idx_session_user ON user_sessions(user_id);
```

## 10. MONITORING & OBSERVABILITY

### 10.1 Logging Strategy
```python
# Structured Logging
import structlog

logger = structlog.get_logger()

class LoggingMiddleware:
    async def log_request(self, request: Request, response: Response):
        logger.info(
            "api_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            response_time=response.headers.get('X-Response-Time'),
            user_agent=request.headers.get('User-Agent')
        )
```

### 10.2 Metrics Collection
```python
# Performance Metrics
class MetricsCollector:
    def __init__(self):
        self.prometheus_client = PrometheusClient()
    
    def record_api_call(self, endpoint: str, duration: float, status_code: int):
        """Record API call metrics"""
        self.prometheus_client.counter('api_calls_total', endpoint=endpoint, status=status_code).inc()
        self.prometheus_client.histogram('api_duration_seconds', endpoint=endpoint).observe(duration)
    
    def record_search_accuracy(self, query: str, accuracy: float):
        """Record search accuracy metrics"""
        self.prometheus_client.gauge('search_accuracy', query_type=query).set(accuracy)
```

## 11. DEPLOYMENT ARCHITECTURE

### 11.1 Container Architecture
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/tariff.db
      - CHROMA_HOST=chromadb
      - OLLAMA_HOST=ollama
    depends_on:
      - chromadb
      - ollama
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
  
  chromadb:
    image: chromadb/chroma
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma
  
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - frontend

volumes:
  chroma_data:
  ollama_data:
```

### 11.2 Environment Configuration
```python
# Configuration Management
class Config:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///./data/tariff.db')
        self.chroma_host = os.getenv('CHROMA_HOST', 'localhost')
        self.ollama_host = os.getenv('OLLAMA_HOST', 'localhost')
        self.serp_api_key = os.getenv('SERP_API_KEY')
        self.avalara_api_key = os.getenv('AVALARA_API_KEY')
        self.max_concurrent_users = int(os.getenv('MAX_CONCURRENT_USERS', '100'))
        self.cache_ttl = int(os.getenv('CACHE_TTL', '3600'))
```

## 12. SCALABILITY CONSIDERATIONS

### 12.1 Horizontal Scaling
- **Load Balancer**: Distribute traffic across multiple backend instances
- **Database Sharding**: Partition data by HTS code ranges
- **Cache Distribution**: Use Redis cluster for distributed caching
- **Microservices**: Split into independent services for better scaling

### 12.2 Performance Optimization
- **Async Processing**: Use async/await for I/O operations
- **Connection Pooling**: Optimize database connections
- **CDN Integration**: Cache static assets globally
- **Background Jobs**: Process heavy calculations asynchronously

## 13. FAILURE HANDLING

### 13.1 Circuit Breaker Pattern
```python
# Circuit Breaker Implementation
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e
```

### 13.2 Fallback Strategies
```python
# Fallback Service
class FallbackService:
    def __init__(self):
        self.fallback_data = self.load_fallback_data()
    
    async def get_tariff_rate_fallback(self, hts_code: str, country: str) -> float:
        """Get tariff rate from fallback data if external API fails"""
        return self.fallback_data.get(f"{hts_code}:{country}", 0.0)
    
    async def get_product_details_fallback(self, query: str) -> ProductDetails:
        """Get product details from local database if SERP API fails"""
        return self.search_local_database(query)
```

This system design provides a robust, scalable, and maintainable architecture for the Tariff Management Chatbot, ensuring high performance, reliability, and user satisfaction. 
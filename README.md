# TariffAI - Intelligent HTS & Tariff Management System

## Overview

TariffAI is a comprehensive tariff management chatbot that provides intelligent HTS code search, tariff calculations, scenario analysis, and alternative sourcing recommendations. The system combines AI-powered search with real-time data to help businesses optimize their international trade operations.

## Features

### 🔍 **Intelligent HTS Search**
- **Semantic Search**: AI-powered search using sentence transformers and ChromaDB
- **Fallback Search**: Direct text search when AI search is unavailable
- **Real-time Results**: Fast search with debounced input
- **Quick Search Tags**: Pre-defined search terms for common products

### 🤖 **AI Assistant**
- **Natural Language Processing**: Chat with the AI about tariffs and trade
- **Context Awareness**: Maintains conversation context
- **Multi-modal Responses**: Text and structured data responses
- **Fallback Handling**: Graceful degradation when AI services are unavailable

### 🧮 **Tariff Calculator**
- **Multi-factor Calculations**: Material cost, shipping, insurance, and duties
- **Currency Conversion**: Real-time currency conversion using forex-python
- **Country-specific Rates**: Support for different countries and trade agreements
- **Detailed Breakdown**: Itemized cost analysis

### 📊 **Scenario Analysis**
- **What-if Analysis**: Compare different sourcing scenarios
- **Cost Optimization**: Find the most cost-effective options
- **Risk Assessment**: Evaluate supply chain risks
- **Visualization**: Charts and graphs for analysis

### 🌍 **Alternative Sourcing**
- **Supplier Discovery**: Find alternative suppliers by country
- **Cost Comparison**: Compare costs across different countries
- **Lead Time Analysis**: Shipping and delivery time estimates
- **Savings Calculation**: Potential cost savings analysis

### 💱 **Currency Converter**
- **Real-time Rates**: Live currency exchange rates
- **Historical Data**: Historical rate tracking
- **Multiple Currencies**: Support for major world currencies
- **API Integration**: Reliable forex data sources

### 📈 **Advanced Analytics**
- **Custom Reports**: Generate detailed trade reports
- **Data Visualization**: Interactive charts and graphs
- **Export Options**: CSV, PDF, and JSON export formats
- **Trend Analysis**: Historical data analysis

### 🔔 **Alert System**
- **Rate Monitoring**: Track tariff rate changes
- **Email Notifications**: Automated email alerts
- **Customizable Alerts**: Set up alerts for specific HTS codes
- **Frequency Control**: Daily, weekly, or monthly alerts

### 📥 **Data Ingestion**
- **Manual Entry**: Add custom HTS codes and descriptions
- **Bulk Import**: Import data from Excel files
- **Validation**: Data quality checks and validation
- **Integration**: Seamless integration with existing data

## Technology Stack

### Backend
- **Framework**: FastAPI with async support
- **Database**: ChromaDB for vector storage
- **AI/ML**: Sentence Transformers, Ollama LLM
- **Currency**: forex-python for exchange rates
- **Data Processing**: Pandas, NumPy

### Frontend
- **Framework**: Vanilla JavaScript with modern CSS
- **Styling**: CSS Grid, Flexbox, Glassmorphism
- **Animations**: CSS animations and transitions
- **Responsive**: Mobile-first design

### Infrastructure
- **Server**: Uvicorn ASGI server
- **CORS**: Cross-origin resource sharing enabled
- **Health Checks**: Comprehensive health monitoring
- **Error Handling**: Graceful error handling and fallbacks

## Quick Start

### Prerequisites
- Python 3.8+
- Ollama (for LLM features)
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tariff-chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Ollama (optional)**
   ```bash
   # Download from https://ollama.ai
   # Install llama3.2:3b model
   ollama pull llama3.2:3b
   ```

### Running the System

1. **Start the backend**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend**
   ```bash
   python -m http.server 3000
   ```

3. **Access the application**
   - Open your browser and go to `http://localhost:3000`
   - The backend API will be available at `http://localhost:8000`

## API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `POST /api/hts/search` - HTS code search
- `POST /api/chat` - AI chat interface

### Tariff Management
- `POST /api/tariff/calculate` - Calculate tariffs
- `POST /api/scenario/simulate` - Scenario analysis
- `POST /api/currency/convert` - Currency conversion

### Sourcing & Analytics
- `POST /api/sourcing/suggest` - Alternative sourcing
- `POST /api/product/search` - Product search
- `POST /api/materials/suggest` - Material suggestions

### Data Management
- `POST /api/data/ingest` - Data ingestion
- `GET /api/hts/codes` - Get HTS codes
- `POST /api/alerts/subscribe` - Alert subscriptions

## Usage Examples

### HTS Code Search
```javascript
// Search for steel products
const response = await fetch('/api/hts/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: 'steel pipes', limit: 10 })
});
```

### Tariff Calculation
```javascript
// Calculate tariff for steel pipes
const response = await fetch('/api/tariff/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        hts_code: '7304.41.00',
        material_cost: 1000,
        country_of_origin: 'China',
        shipping_cost: 200
    })
});
```

### Alternative Sourcing
```javascript
// Find alternative sources
const response = await fetch('/api/sourcing/suggest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        hts_code: '7304.41.00',
        current_country: 'China'
    })
});
```

## Configuration

### Environment Variables
- `OLLAMA_BASE_URL`: Ollama server URL (default: http://localhost:11434)
- `CHROMA_DB_PATH`: ChromaDB storage path (default: ./data/chroma)
- `EXCEL_DATA_PATH`: Excel file path (default: ./data/tariff_database_2025.xlsx)

### Data Sources
The system uses a comprehensive tariff database with:
- 12,912 HTS codes
- 122 data columns
- Multiple country rates
- Trade agreement information

## System Architecture

### Data Flow
1. **User Input** → Frontend validation
2. **API Request** → FastAPI backend
3. **AI Processing** → Sentence transformers + ChromaDB
4. **Fallback** → Direct text search if AI unavailable
5. **Response** → Structured data + UI updates

### AI Components
- **Embedding Model**: all-MiniLM-L6-v2 for semantic search
- **LLM**: Ollama with llama3.2:3b model
- **Vector Database**: ChromaDB for similarity search
- **Fallback**: Fuzzy string matching

### Performance Optimizations
- **Debounced Search**: 500ms delay to reduce API calls
- **Caching**: ChromaDB for fast vector search
- **Async Processing**: Non-blocking API calls
- **Batch Processing**: Efficient data indexing

## Troubleshooting

### Common Issues

1. **Backend not starting**
   - Check if port 8000 is available
   - Verify Python dependencies are installed
   - Check for missing data files

2. **AI features not working**
   - Ensure Ollama is running
   - Verify llama3.2:3b model is installed
   - Check Ollama API connectivity

3. **Search not returning results**
   - Verify Excel data file exists
   - Check ChromaDB initialization
   - Ensure data indexing completed

4. **Frontend not loading**
   - Check if port 3000 is available
   - Verify backend is running
   - Check browser console for errors

### Debug Mode
Enable debug logging by setting the log level:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Development

### Project Structure
```
tariff-chatbot/
├── main.py                 # Main FastAPI application
├── index.html             # Frontend interface
├── requirements.txt       # Python dependencies
├── data/                  # Data storage
│   ├── chroma/           # ChromaDB files
│   └── tariff_database_2025.xlsx
├── database/             # Database schemas
├── exports/              # Generated reports
├── uploads/              # File uploads
└── docs/                 # Documentation
```

### Adding New Features
1. **Backend**: Add new endpoints in `main.py`
2. **Frontend**: Update `index.html` with new UI components
3. **Testing**: Create test scripts for new functionality
4. **Documentation**: Update README and API docs

### Code Style
- **Python**: PEP 8 compliance
- **JavaScript**: ES6+ with modern syntax
- **CSS**: BEM methodology for class naming
- **Comments**: Comprehensive docstrings and inline comments

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation

## Roadmap

See [FUTURE_FEATURES_ROADMAP.md](FUTURE_FEATURES_ROADMAP.md) for planned features and implementation strategies.

---

**TariffAI** - Making international trade smarter and more efficient. 
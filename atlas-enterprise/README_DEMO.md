# 🌟 ATLAS Enterprise - Proof of Concept Demo

## Overview

ATLAS Enterprise is an intelligent tariff management and trade compliance platform that demonstrates comprehensive functionality across three key user personas:

- **🏢 Procurement Managers**: Cost optimization and sourcing analysis
- **🛡️ Compliance Officers**: Regulatory compliance and risk management  
- **📊 Business Analysts**: Strategic insights and AI-powered analysis

## 🚀 Quick Start Guide

### Prerequisites

1. **Python 3.11+** with pip
2. **Node.js 18+** with npm
3. **Ollama** (for AI features) - Download from [ollama.ai](https://ollama.ai)

### Installation & Setup

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository>
   cd atlas-enterprise
   ```

2. **Install backend dependencies:**
   ```bash
   cd backend
   pip install -r requirements_unified.txt
   cd ..
   ```

3. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Start Ollama (in a separate terminal):**
   ```bash
   ollama serve
   ```

5. **Pull required models:**
   ```bash
   ollama pull llama3.1
   ollama pull llama3.2:3b
   ollama pull qwen3:8b
   ```

### 🎬 Start the Demo

**Option 1: Automated Startup (Recommended)**
```bash
python start_atlas_demo.py
```

**Option 2: Manual Startup**

Terminal 1 (Backend):
```bash
cd backend
python -m uvicorn main_unified:app --host 0.0.0.0 --port 8000 --reload
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

### 📍 Access Points

- **🎨 Frontend Application**: http://localhost:3000
- **🔧 Backend API**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs
- **🤖 AI Service**: http://localhost:11434 (Ollama)

## 🎯 Demo Features

### 🏢 Procurement Manager View

**Product Classification & Costing**
- Real-time HTS code search across 12,900+ codes
- Instant tariff calculations with duty rates
- Multi-country sourcing cost comparison
- Section 301 tariff impact analysis

**Key Capabilities:**
- Search products by description (e.g., "laptop", "smartphone")
- Calculate total landed costs including duties, MPF, HMF
- Compare sourcing options across China, Vietnam, Mexico, India
- Real-time cost optimization recommendations

### 🛡️ Compliance Officer View

**Regulatory Compliance Dashboard**
- Active compliance alerts and notifications
- Compliance score breakdown with metrics
- HTS classification accuracy tracking
- Documentation completeness monitoring

**Key Capabilities:**
- Section 301 tariff update notifications
- Certificate of origin requirement tracking
- GSP benefit eligibility alerts
- Audit readiness scoring

### 📊 Business Analyst View

**AI-Powered Trade Intelligence**
- Natural language queries about trade regulations
- Strategic sourcing recommendations
- Risk assessment and trend analysis
- Cost savings opportunity identification

**Key Capabilities:**
- Ask AI about tariff regulations and compliance
- Analyze trade data patterns and trends
- Generate strategic sourcing reports
- Identify cost optimization opportunities

## 🗂️ Data Sources

### Real Data Integration

1. **HTS Tariff Database**: 12,900+ real HTS codes with current duty rates
2. **Trade Regulations**: Current Section 301, GSP, and FTA information
3. **Country-Specific Data**: Duty rates, lead times, and risk assessments
4. **AI Knowledge Base**: Trade compliance and regulatory guidance

### File Structure
```
atlas-enterprise/
├── backend/
│   ├── main_unified.py          # Unified backend with all features
│   ├── data/
│   │   ├── tariff_database_2025.xlsx    # Real HTS data (12,900+ codes)
│   │   ├── tariff_management_kb.json    # Trade knowledge base
│   │   └── chroma/                      # Vector search database
│   └── requirements_unified.txt         # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/UnifiedDashboard.tsx   # Main demo dashboard
│   │   ├── hooks/useHTS.ts             # HTS search integration
│   │   └── hooks/useAI.ts              # AI chat integration
│   └── package.json                     # Node.js dependencies
└── start_atlas_demo.py                  # Demo startup script
```

## 🧪 Testing the Demo

### 1. HTS Search & Classification
- Search for "computer" or "smartphone"
- Select an HTS code and calculate tariffs
- Try different product values to see cost impacts

### 2. AI Trade Intelligence
- Ask: "What are Section 301 tariffs?"
- Ask: "Compare sourcing costs between China and Vietnam"
- Ask: "What are compliance requirements for electronics?"

### 3. Multi-Country Sourcing Analysis
- Select different countries in sourcing options
- Compare total landed costs including duties
- Review risk assessments and lead times

### 4. Compliance Monitoring
- Review active compliance alerts
- Check compliance score breakdowns
- Explore regulatory update notifications

## 🔧 Technical Architecture

### Backend (FastAPI + Python)
- **Real Data Processing**: Pandas for Excel data handling
- **Vector Search**: ChromaDB for semantic knowledge search
- **AI Integration**: Direct Ollama API integration
- **API Design**: RESTful endpoints with OpenAPI documentation

### Frontend (React + TypeScript)
- **Modern UI**: Tailwind CSS with shadcn/ui components
- **State Management**: TanStack Query for API state
- **Real-time Updates**: Live search and calculation updates
- **Responsive Design**: Works across desktop and tablet

### AI & ML Integration
- **Local LLMs**: Ollama with multiple model support
- **Knowledge Base**: Vector embeddings for trade information
- **Semantic Search**: ChromaDB for intelligent document retrieval
- **Future Ready**: Extensible for Groq, OpenAI, Google APIs

## 🎯 Business Value Demonstration

### For CFOs
- **Cost Savings**: Identify $125K+ in potential duty savings
- **Risk Mitigation**: Reduce tariff exposure through sourcing diversification
- **ROI Analysis**: Calculate total landed costs with precision

### For COOs
- **Supply Chain Optimization**: Compare lead times and costs across countries
- **Risk Assessment**: Evaluate supplier and country-specific risks
- **Operational Efficiency**: Streamline import/export processes

### For CCOs
- **Compliance Assurance**: 94% compliance score with real-time monitoring
- **Regulatory Updates**: Automated alerts for tariff and regulation changes
- **Audit Readiness**: Comprehensive documentation and classification accuracy

## 🚀 Future Roadmap

### Phase 2: Enhanced AI Agents
- **Sourcing Advisor Agent**: Autonomous sourcing recommendations
- **Compliance Agent**: Automated classification and risk detection
- **Cost Optimization Agent**: Dynamic pricing and duty optimization

### Phase 3: External API Integration
- **Real-time Forex**: Live exchange rate integration
- **Supplier APIs**: Direct supplier cost and availability data
- **Regulatory APIs**: OFAC, WTO, and customs database integration

### Phase 4: Advanced Analytics
- **Predictive Modeling**: Forecast tariff changes and market trends
- **Risk Scoring**: Advanced supplier and country risk assessment
- **Strategic Planning**: Long-term sourcing and compliance strategies

## 🛠️ Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   - Ensure Ollama is running: `ollama serve`
   - Check models are installed: `ollama list`
   - Verify port 11434 is available

2. **Frontend Not Loading**
   - Check if port 3000 is available
   - Ensure npm dependencies are installed
   - Verify backend is running on port 8000

3. **Backend API Errors**
   - Check Python dependencies are installed
   - Verify Excel data file exists in `backend/data/`
   - Check port 8000 is available

4. **Search Returns No Results**
   - Try broader search terms (e.g., "computer" instead of "laptop")
   - Check if HTS data loaded successfully in backend logs
   - Verify Excel file has correct column structure

### Debug Commands

```bash
# Check backend health
curl http://localhost:8000/health

# Test HTS search
curl "http://localhost:8000/api/v1/tariff/hts/search?query=computer&limit=3"

# Check Ollama status
curl http://localhost:11434/api/tags

# View backend logs
cd backend && python main_unified.py
```

## 📞 Support

For technical support or questions about the demo:
- Review API documentation at http://localhost:8000/docs
- Check backend logs for detailed error messages
- Ensure all prerequisites are properly installed

---

**🌟 ATLAS Enterprise - Transforming Trade Intelligence with AI** 
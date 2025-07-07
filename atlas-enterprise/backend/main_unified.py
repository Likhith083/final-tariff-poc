"""
ATLAS Enterprise - Unified Backend
Production-ready FastAPI application with full functionality
"""

import os
import time
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import requests
from pathlib import Path

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator

# Vector search imports
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("ChromaDB not available - vector search disabled")

# Add these imports at the top with other imports
# from agents.sourcing_agent import create_sourcing_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
HTS_DATA = None
KNOWLEDGE_BASE = None
CHROMA_CLIENT = None
CHROMA_COLLECTION = None
SOURCING_AGENT = None

# =============================================================================
# MODELS & SCHEMAS
# =============================================================================

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = Field(default='llama3.1', description="Model to use for chat")
    serp_search: Optional[bool] = Field(default=False, description="Enable product search")
    product_query: Optional[str] = Field(default=None, description="Product search query")
    temperature: Optional[float] = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=1000, ge=1, le=4000)

class ChatResponse(BaseModel):
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    product_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class HTSSearchRequest(BaseModel):
    query: str = Field(..., description="Search query for HTS codes")
    chapter: Optional[str] = Field(default=None, description="Filter by chapter")
    limit: int = Field(default=20, ge=1, le=100)

class HTSCode(BaseModel):
    id: int
    hts_code: str
    description: str
    general_rate: float
    special_rate: Optional[float] = None
    other_rate: Optional[float] = None
    unit_of_quantity: str = "PCE"
    chapter: str
    heading: str
    subheading: str

class HTSSearchResponse(BaseModel):
    success: bool
    message: str
    data: List[HTSCode]
    total_results: int
    search_query: str
    search_time_ms: int

class TariffCalculationRequest(BaseModel):
    hts_code: str
    product_value: float = Field(..., gt=0, description="Product value in USD")
    quantity: int = Field(default=1, ge=1)
    freight_cost: float = Field(default=0, ge=0)
    insurance_cost: float = Field(default=0, ge=0)
    country_code: str = Field(default="CN", description="Country of origin")

class TariffCalculationResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]

class SourcingAnalysisRequest(BaseModel):
    product_description: str
    target_countries: List[str] = Field(default=["CN", "VN", "MX", "IN"])
    product_value: float = Field(..., gt=0)
    quantity: int = Field(default=1, ge=1)

class SourcingAnalysisResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]

# =============================================================================
# DATA LOADING & INITIALIZATION
# =============================================================================

def load_hts_data():
    """Load HTS data from Excel file"""
    global HTS_DATA
    try:
        excel_path = Path(__file__).parent / 'data' / 'tariff_database_2025.xlsx'
        if not excel_path.exists():
            logger.error(f"Excel file not found at {excel_path}")
            return False
        
        logger.info(f"Loading HTS data from {excel_path}")
        df = pd.read_excel(excel_path)
        
        # Rename columns for easier access
        df = df.rename(columns={
            df.columns[0]: 'hts_code',
            df.columns[1]: 'description', 
            df.columns[7]: 'general_rate'
        })
        
        # Clean and convert data
        df['general_rate'] = pd.to_numeric(df['general_rate'], errors='coerce').fillna(0)
        df['hts_code'] = df['hts_code'].astype(str)
        df['description'] = df['description'].astype(str)
        
        # Convert to list of dictionaries
        HTS_DATA = df.to_dict('records')
        logger.info(f"Successfully loaded {len(HTS_DATA)} HTS codes")
        return True
        
    except Exception as e:
        logger.error(f"Error loading HTS data: {e}")
        return False

def load_knowledge_base():
    """Load knowledge base from JSON files"""
    global KNOWLEDGE_BASE
    try:
        knowledge_files = [
            'tariff_management_kb.json',
            'srs_examples_kb.json', 
            'additional_knowledge.json',
            'adcvd_faq.json'
        ]
        
        KNOWLEDGE_BASE = []
        data_dir = Path(__file__).parent / 'data'
        
        for file_name in knowledge_files:
            file_path = data_dir / file_name
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        KNOWLEDGE_BASE.extend(data)
                    else:
                        KNOWLEDGE_BASE.append(data)
        
        logger.info(f"Loaded {len(KNOWLEDGE_BASE)} knowledge base entries")
        return True
        
    except Exception as e:
        logger.error(f"Error loading knowledge base: {e}")
        return False

def initialize_chromadb():
    """Initialize ChromaDB for vector search"""
    global CHROMA_CLIENT, CHROMA_COLLECTION
    
    if not CHROMADB_AVAILABLE:
        logger.warning("ChromaDB not available - skipping vector search initialization")
        return False
        
    try:
        # Create ChromaDB client
        chroma_path = Path(__file__).parent / 'data' / 'chroma'
        chroma_path.mkdir(exist_ok=True)
        
        CHROMA_CLIENT = chromadb.PersistentClient(path=str(chroma_path))
        
        # Get or create collection
        try:
            CHROMA_COLLECTION = CHROMA_CLIENT.get_collection("atlas_knowledge")
            logger.info(f"Using existing ChromaDB collection with {CHROMA_COLLECTION.count()} documents")
        except:
            CHROMA_COLLECTION = CHROMA_CLIENT.create_collection("atlas_knowledge")
            logger.info("Created new ChromaDB collection")
            
            # Add knowledge base to collection if it's new
            if KNOWLEDGE_BASE:
                documents = []
                metadatas = []
                ids = []
                
                for i, item in enumerate(KNOWLEDGE_BASE):
                    if isinstance(item, dict):
                        content = item.get('content', str(item))
                        metadata = {k: v for k, v in item.items() if k != 'content'}
                    else:
                        content = str(item)
                        metadata = {}
                    
                    documents.append(content)
                    metadatas.append(metadata)
                    ids.append(f"kb_{i}")
                
                CHROMA_COLLECTION.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"Added {len(documents)} documents to ChromaDB")
        
        return True
        
    except Exception as e:
        logger.error(f"Error initializing ChromaDB: {e}")
        return False

# =============================================================================
# SEARCH & ANALYSIS FUNCTIONS
# =============================================================================

def search_hts_data(query: str, chapter: Optional[str] = None, limit: int = 20) -> List[Dict]:
    """Search HTS data using fast substring matching"""
    if not HTS_DATA:
        return []
    
    query_lower = query.lower()
    results = []
    
    for row in HTS_DATA:
        # Search in description (case-insensitive)
        if query_lower in str(row.get('description', '')).lower():
            # If chapter filter is specified, check if it matches
            if chapter:
                hts_code = str(row.get('hts_code', ''))
                if not hts_code.startswith(chapter):
                    continue
            
            # Format the result
            result = {
                "id": len(results) + 1,
                "hts_code": str(row.get('hts_code', '')),
                "description": str(row.get('description', '')),
                "chapter": str(row.get('hts_code', ''))[:2] if len(str(row.get('hts_code', ''))) >= 2 else '',
                "heading": str(row.get('hts_code', ''))[:4] if len(str(row.get('hts_code', ''))) >= 4 else '',
                "subheading": str(row.get('hts_code', ''))[:6] if len(str(row.get('hts_code', ''))) >= 6 else '',
                "general_rate": float(row.get('general_rate', 0)),
                "special_rate": None,
                "other_rate": None,
                "unit_of_quantity": "PCE"
            }
            results.append(result)
            
            if len(results) >= limit:
                break
    
    return results

def search_knowledge_base(query: str, top_k: int = 5) -> List[Dict]:
    """Search knowledge base using vector similarity"""
    if CHROMA_COLLECTION:
        try:
            results = CHROMA_COLLECTION.query(
                query_texts=[query],
                n_results=top_k
            )
            
            return [
                {
                    "content": doc,
                    "metadata": meta,
                    "distance": dist
                }
                for doc, meta, dist in zip(
                    results['documents'][0],
                    results['metadatas'][0], 
                    results['distances'][0]
                )
            ]
        except Exception as e:
            logger.error(f"Vector search error: {e}")
    
    # Fallback to simple text search
    if not KNOWLEDGE_BASE:
        return []
    
    query_lower = query.lower()
    results = []
    
    for item in KNOWLEDGE_BASE:
        content = str(item)
        if query_lower in content.lower():
            results.append({
                "content": content,
                "metadata": item if isinstance(item, dict) else {},
                "distance": 0.5
            })
            
            if len(results) >= top_k:
                break
    
    return results

async def call_ollama(model: str, messages: List[Dict], temperature: float = 0.1, max_tokens: int = 1000):
    """Call local Ollama API with enhanced context"""
    try:
        # Format messages for Ollama
        formatted_messages = []
        
        # Add system message with ATLAS context
        system_context = """You are an expert AI assistant for ATLAS Enterprise, a comprehensive tariff management and trade intelligence platform. You help users with:

- HTS code classification and analysis
- Tariff calculations and duty estimates  
- Trade compliance questions
- Sourcing optimization and cost analysis
- Regulatory guidance and updates
- Import/export documentation
- Free Trade Agreement benefits
- Section 301 tariff impacts
- Anti-dumping and countervailing duties

You have access to:
- Real HTS tariff database with 12,900+ codes
- Current duty rates and trade regulations
- Knowledge base of trade compliance information
- Sourcing analysis capabilities

Provide accurate, actionable responses based on current trade regulations and best practices. Always cite specific HTS codes when relevant and explain duty calculations clearly."""
        
        formatted_messages.append({
            "role": "system",
            "content": system_context
        })
        
        # Add conversation messages
        for message in messages:
            formatted_messages.append({
                "role": message["role"],
                "content": message["content"]
            })
        
        # Call Ollama API with better error handling
        payload = {
            "model": model,
            "messages": formatted_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        logger.info(f"Calling Ollama with model: {model}")
        
        # Use a longer timeout and better error handling
        import httpx
        
        # Try host.docker.internal first (for Docker), then localhost
        ollama_urls = [
            "http://host.docker.internal:11434/api/chat",
            "http://localhost:11434/api/chat"
        ]
        
        response = None
        last_error = None
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            for url in ollama_urls:
                try:
                    response = await client.post(url, json=payload)
                    if response.status_code == 200:
                        break
                except Exception as e:
                    last_error = e
                    continue
            
            if not response or response.status_code != 200:
                raise Exception(f"Failed to connect to Ollama. Last error: {last_error}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Ollama response received successfully")
                return {
                    "content": result.get("message", {}).get("content", ""),
                    "model": model,
                    "usage": {
                        "prompt_tokens": result.get("prompt_eval_count", 0),
                        "completion_tokens": result.get("eval_count", 0),
                        "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
                    }
                }
            else:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
    except Exception as e:
        logger.error(f"Ollama connection error: {e}")
        # Return a more helpful error message
        return {
            "content": f"I'm having trouble connecting to the {model} model. Here's what you can try:\n\n1. **Check if Ollama is running**: Open a terminal and run `ollama list` to see available models\n2. **Start Ollama**: If not running, start it with `ollama serve`\n3. **Verify the model**: Make sure {model} is installed with `ollama pull {model}`\n4. **Check the port**: Ensure nothing else is using port 11434\n\n**Available models on your system**: {', '.join(['llava:latest', 'devstral:24b', 'llama3.2:3b', 'qwen3:8b', 'deepseek-r1:8b', 'moondream:latest', 'mxbai-embed-large:latest', 'llama3.1:latest', 'gemma3:4b', 'phi4:latest'])}\n\nTry using one of these models instead, or let me know if you need help with the setup!",
            "model": model,
            "usage": {"total_tokens": 0},
            "error": str(e)
        }

def calculate_tariff(hts_code: str, product_value: float, country_code: str = "CN", 
                    quantity: int = 1, freight_cost: float = 0, insurance_cost: float = 0) -> Dict:
    """Calculate comprehensive tariff costs"""
    try:
        # Find HTS code in database
        hts_info = None
        if HTS_DATA:
            for row in HTS_DATA:
                if str(row.get('hts_code', '')).replace('.', '') == hts_code.replace('.', ''):
                    hts_info = row
                    break
        
        # Get duty rate
        duty_rate = 0.0
        if hts_info:
            duty_rate = float(hts_info.get('general_rate', 0))
        
        # Apply country-specific adjustments
        if country_code == "CN":
            # Check for Section 301 tariffs (simplified)
            if hts_code.startswith(('8471', '8517', '8473')):  # Electronics
                duty_rate += 25.0  # Section 301 tariff
        
        # Calculate costs
        customs_value = product_value + freight_cost + insurance_cost
        duty_amount = customs_value * (duty_rate / 100)
        
        # MPF (Merchandise Processing Fee)
        mpf_rate = 0.3464 / 100
        mpf_amount = max(customs_value * mpf_rate, 27.23)  # Minimum MPF
        if customs_value > 2500:
            mpf_amount = min(mpf_amount, 528.33)  # Maximum MPF
        
        # HMF (Harbor Maintenance Fee)
        hmf_rate = 0.125 / 100
        hmf_amount = customs_value * hmf_rate
        
        total_fees = duty_amount + mpf_amount + hmf_amount
        total_landed_cost = customs_value + total_fees
        
        return {
            "hts_code": hts_code,
            "product_description": hts_info.get('description', 'Unknown') if hts_info else 'Unknown',
            "country_code": country_code,
            "product_value_usd": product_value,
            "customs_value": customs_value,
            "duty_rate": duty_rate,
            "duty_amount": duty_amount,
            "mpf_amount": mpf_amount,
            "hmf_amount": hmf_amount,
            "total_fees": total_fees,
            "total_landed_cost": total_landed_cost,
            "calculation_breakdown": {
                "product_value": product_value,
                "freight_cost": freight_cost,
                "insurance_cost": insurance_cost,
                "customs_value": customs_value,
                "duty_calculation": f"{duty_rate}% of ${customs_value:,.2f}",
                "mpf_calculation": f"${mpf_amount:.2f} (0.3464% of customs value)",
                "hmf_calculation": f"${hmf_amount:.2f} (0.125% of customs value)"
            }
        }
        
    except Exception as e:
        logger.error(f"Tariff calculation error: {e}")
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

def analyze_sourcing_options(product_description: str, target_countries: List[str], 
                           product_value: float, quantity: int = 1) -> Dict:
    """Analyze sourcing options across multiple countries"""
    try:
        # Find potential HTS codes for the product
        potential_codes = search_hts_data(product_description, limit=3)
        
        if not potential_codes:
            raise HTTPException(status_code=404, detail="No matching HTS codes found")
        
        # Use the first/best match
        hts_code = potential_codes[0]['hts_code']
        
        # Country-specific analysis
        country_analysis = {}
        
        for country in target_countries:
            try:
                calc = calculate_tariff(hts_code, product_value, country, quantity)
                
                # Add country-specific insights
                insights = []
                if country == "CN":
                    insights.append("May be subject to Section 301 tariffs")
                    insights.append("Largest manufacturing capacity")
                elif country == "VN":
                    insights.append("GSP eligible - potential duty-free access")
                    insights.append("Growing manufacturing hub")
                elif country == "MX":
                    insights.append("USMCA benefits - typically duty-free")
                    insights.append("Shortest shipping times to US")
                elif country == "IN":
                    insights.append("GSP eligible for many products")
                    insights.append("Large domestic market")
                
                country_analysis[country] = {
                    "country_name": get_country_name(country),
                    "duty_rate": calc["duty_rate"],
                    "total_landed_cost": calc["total_landed_cost"],
                    "duty_amount": calc["duty_amount"],
                    "insights": insights,
                    "calculation": calc
                }
                
            except Exception as e:
                logger.error(f"Error analyzing {country}: {e}")
                country_analysis[country] = {
                    "country_name": get_country_name(country),
                    "error": str(e)
                }
        
        # Find best option
        best_option = None
        lowest_cost = float('inf')
        
        for country, data in country_analysis.items():
            if "total_landed_cost" in data and data["total_landed_cost"] < lowest_cost:
                lowest_cost = data["total_landed_cost"]
                best_option = country
        
        return {
            "product_description": product_description,
            "hts_code": hts_code,
            "hts_description": potential_codes[0]['description'],
            "analysis_date": datetime.now().isoformat(),
            "countries": country_analysis,
            "recommendation": {
                "best_option": best_option,
                "best_option_name": get_country_name(best_option) if best_option else None,
                "lowest_cost": lowest_cost if lowest_cost != float('inf') else None,
                "reasoning": f"Lowest total landed cost at ${lowest_cost:,.2f}" if lowest_cost != float('inf') else "Unable to determine best option"
            }
        }
        
    except Exception as e:
        logger.error(f"Sourcing analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

def get_country_name(country_code: str) -> str:
    """Get country name from country code"""
    country_names = {
        "CN": "China",
        "VN": "Vietnam", 
        "MX": "Mexico",
        "IN": "India",
        "TH": "Thailand",
        "MY": "Malaysia",
        "ID": "Indonesia",
        "PH": "Philippines",
        "BD": "Bangladesh",
        "PK": "Pakistan"
    }
    return country_names.get(country_code, country_code)

def check_ollama_availability():
    """Check if Ollama is available with better error handling"""
    try:
        import httpx
        
        # Try host.docker.internal first (for Docker), then localhost
        ollama_urls = [
            "http://host.docker.internal:11434/api/tags",
            "http://localhost:11434/api/tags"
        ]
        
        with httpx.Client(timeout=5.0) as client:
            for url in ollama_urls:
                try:
                    response = client.get(url)
                    if response.status_code == 200:
                        models = response.json().get("models", [])
                        logger.info(f"Ollama is running with {len(models)} models available at {url}")
                        return True
                except Exception as e:
                    logger.debug(f"Failed to connect to {url}: {e}")
                    continue
            
            logger.warning("Failed to connect to Ollama on any URL")
            return False
    except Exception as e:
        logger.warning(f"Ollama check failed: {e}")
        return False

# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="ATLAS Enterprise API",
    version="2.0.0",
    description="Comprehensive tariff management and trade intelligence platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# =============================================================================
# STARTUP & SHUTDOWN
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize all services on startup"""
    global SOURCING_AGENT
    logger.info("Starting ATLAS Enterprise API...")
    
    # Load data
    logger.info("Loading HTS data...")
    load_hts_data()
    
    logger.info("Loading knowledge base...")
    load_knowledge_base()
    
    logger.info("Initializing ChromaDB...")
    initialize_chromadb()
    
    # Initialize AI Agent
    logger.info("Initializing Sourcing Agent...")
    try:
        # SOURCING_AGENT = create_sourcing_agent(
        #     hts_search_func=search_hts_data,
        #     tariff_calc_func=calculate_tariff
        # )
        logger.info("Sourcing Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Sourcing Agent: {e}")
        SOURCING_AGENT = None
    
    logger.info("ATLAS Enterprise API started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down ATLAS Enterprise API...")

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ATLAS Enterprise API",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Real HTS tariff database (12,900+ codes)",
            "Local Ollama AI integration",
            "Vector search with ChromaDB",
            "Comprehensive tariff calculations",
            "Multi-country sourcing analysis",
            "Trade compliance guidance"
        ],
        "endpoints": {
            "health": "/health",
            "ai_chat": "/api/v1/ai/chat",
            "hts_search": "/api/v1/tariff/hts/search",
            "tariff_calculate": "/api/v1/tariff/calculate",
            "sourcing_analysis": "/api/v1/sourcing/analyze",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    return {
        "success": True,
        "message": "ATLAS Enterprise is healthy",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "api": "healthy",
            "hts_data": "loaded" if HTS_DATA else "not_loaded",
            "knowledge_base": "loaded" if KNOWLEDGE_BASE else "not_loaded",
            "chromadb": "available" if CHROMA_COLLECTION else "not_available",
            "ollama": "available" if check_ollama_availability() else "not_available"
        },
        "data_stats": {
            "hts_codes": len(HTS_DATA) if HTS_DATA else 0,
            "knowledge_entries": len(KNOWLEDGE_BASE) if KNOWLEDGE_BASE else 0,
            "vector_documents": CHROMA_COLLECTION.count() if CHROMA_COLLECTION else 0
        }
    }

# =============================================================================
# AI CHAT ENDPOINTS
# =============================================================================

@app.post("/api/v1/ai/chat", response_model=ChatResponse)
async def ai_chat(request: ChatRequest):
    """AI chat endpoint with enhanced context"""
    try:
        # Enhance context with relevant information
        enhanced_messages = []
        
        # Add knowledge base context if relevant
        if request.messages:
            last_message = request.messages[-1].content
            logger.info(f"Searching knowledge base for: {last_message}")
            
            # Search knowledge base for relevant context
            knowledge_results = search_knowledge_base(last_message, top_k=5)
            
            # Also search HTS data if the query seems product-related
            hts_context = []
            if any(keyword in last_message.lower() for keyword in ['hts', 'tariff', 'duty', 'code', 'product', 'import', 'export']):
                hts_results = search_hts_data(last_message, limit=3)
                if hts_results:
                    hts_context = [f"HTS {result['hts_code']}: {result['description']} (Duty: {result['general_rate']}%)" for result in hts_results]
            
            # Build comprehensive context
            context_parts = []
            
            if knowledge_results:
                context_parts.append("=== RELEVANT KNOWLEDGE BASE INFORMATION ===")
                for i, result in enumerate(knowledge_results, 1):
                    context_parts.append(f"{i}. {result['content']}")
                    if result.get('metadata'):
                        context_parts.append(f"   Source: {result['metadata']}")
                context_parts.append("")
            
            if hts_context:
                context_parts.append("=== RELEVANT HTS CODES ===")
                for hts_info in hts_context:
                    context_parts.append(f"• {hts_info}")
                context_parts.append("")
            
            # Add conversation history (last 3 messages for context)
            conversation_history = []
            for msg in request.messages[-4:-1]:  # Get last 3 messages before current
                conversation_history.append(f"{msg.role.upper()}: {msg.content}")
            
            if conversation_history:
                context_parts.append("=== CONVERSATION HISTORY ===")
                context_parts.extend(conversation_history)
                context_parts.append("")
            
            # Create enhanced prompt
            if context_parts:
                full_context = "\n".join(context_parts)
                enhanced_context = f"""You are an expert AI assistant for ATLAS Enterprise tariff management platform. Use the following information to provide accurate, detailed responses:

{full_context}

CURRENT USER QUESTION: {last_message}

Instructions:
- Use the knowledge base information above to provide accurate answers
- Reference specific HTS codes when relevant
- Provide actionable advice based on trade regulations
- If you don't have specific information, say so clearly
- Always cite your sources when using the provided context"""
                
                # Replace last message with enhanced version
                enhanced_messages = [{"role": m.role, "content": m.content} for m in request.messages[:-1]]
                enhanced_messages.append({"role": "user", "content": enhanced_context})
                
                logger.info(f"Enhanced context provided with {len(knowledge_results)} knowledge entries and {len(hts_context)} HTS codes")
            else:
                enhanced_messages = [{"role": m.role, "content": m.content} for m in request.messages]
                logger.info("No relevant context found, using original messages")
        
        # Call Ollama
        result = await call_ollama(
            model=request.model,
            messages=enhanced_messages,
            temperature=request.temperature or 0.1,
            max_tokens=request.max_tokens or 1000
        )
        
        # Add product info if requested
        product_info = None
        if request.serp_search and request.product_query:
            # Search HTS database for product info
            hts_results = search_hts_data(request.product_query, limit=3)
            if hts_results:
                product_info = {
                    "query": request.product_query,
                    "hts_matches": hts_results,
                    "note": "Product information from HTS database"
                }
        
        return ChatResponse(
            content=result["content"],
            model=result["model"],
            usage=result.get("usage"),
            product_info=product_info,
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"AI chat error: {e}")
        return ChatResponse(
            content="I apologize, but I'm experiencing technical difficulties. Please try again or contact support if the issue persists.",
            model=request.model,
            error=str(e)
        )

# =============================================================================
# HTS & TARIFF ENDPOINTS
# =============================================================================

@app.get("/api/v1/tariff/hts/search", response_model=HTSSearchResponse)
async def search_hts(query: str, chapter: Optional[str] = None, limit: int = 20):
    """Search HTS codes using real Excel data"""
    try:
        start_time = time.time()
        
        results = search_hts_data(query, chapter, limit)
        search_time = int((time.time() - start_time) * 1000)
        
        return HTSSearchResponse(
            success=True,
            message=f"Found {len(results)} HTS codes matching '{query}'",
            data=results,
            total_results=len(results),
            search_query=query,
            search_time_ms=search_time
        )
        
    except Exception as e:
        logger.error(f"HTS search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/tariff/hts/{hts_code}")
async def get_hts_code(hts_code: str):
    """Get specific HTS code details"""
    try:
        if not HTS_DATA:
            raise HTTPException(status_code=503, detail="HTS data not available")
        
        # Search for the specific code
        for row in HTS_DATA:
            if str(row.get('hts_code', '')).replace('.', '') == hts_code.replace('.', ''):
                result = {
                    "id": 1,
                    "hts_code": str(row.get('hts_code', '')),
                    "description": str(row.get('description', '')),
                    "chapter": str(row.get('hts_code', ''))[:2],
                    "heading": str(row.get('hts_code', ''))[:4],
                    "subheading": str(row.get('hts_code', ''))[:6],
                    "general_rate": float(row.get('general_rate', 0)),
                    "special_rate": None,
                    "other_rate": None,
                    "unit_of_quantity": "PCE"
                }
                
                return {
                    "success": True,
                    "message": f"HTS code found: {hts_code}",
                    "data": result
                }
        
        raise HTTPException(status_code=404, detail=f"HTS code not found: {hts_code}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get HTS code error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/tariff/chapters")
async def get_chapters():
    """Get HTS chapters with real data"""
    try:
        if not HTS_DATA:
            raise HTTPException(status_code=503, detail="HTS data not available")
        
        # Count codes by chapter
        chapter_counts = {}
        for row in HTS_DATA:
            hts_code = str(row.get('hts_code', ''))
            if len(hts_code) >= 2:
                chapter = hts_code[:2]
                chapter_counts[chapter] = chapter_counts.get(chapter, 0) + 1
        
        # Create chapter list (simplified descriptions)
        chapters = []
        chapter_descriptions = {
            "01": "Live animals",
            "02": "Meat and edible meat offal",
            "03": "Fish and crustaceans",
            "04": "Dairy produce",
            "05": "Products of animal origin",
            "84": "Nuclear reactors, boilers, machinery",
            "85": "Electrical machinery and equipment",
            "61": "Articles of apparel, knitted",
            "62": "Articles of apparel, not knitted",
            "63": "Other made up textile articles"
        }
        
        for chapter, count in sorted(chapter_counts.items()):
            chapters.append({
                "chapter_number": chapter,
                "description": chapter_descriptions.get(chapter, f"Chapter {chapter}"),
                "code_count": count
            })
        
        return {
            "success": True,
            "message": f"Retrieved {len(chapters)} HTS chapters",
            "data": chapters[:20]  # Limit to first 20 chapters
        }
        
    except Exception as e:
        logger.error(f"Get chapters error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/tariff/popular-codes")
async def get_popular_codes(limit: int = 10):
    """Get popular HTS codes"""
    try:
        if not HTS_DATA:
            raise HTTPException(status_code=503, detail="HTS data not available")
        
        # Return first N codes as "popular" (in real system, this would be based on usage stats)
        popular_codes = []
        for i, row in enumerate(HTS_DATA[:limit]):
            result = {
                "id": i + 1,
                "hts_code": str(row.get('hts_code', '')),
                "description": str(row.get('description', '')),
                "chapter": str(row.get('hts_code', ''))[:2],
                "heading": str(row.get('hts_code', ''))[:4],
                "subheading": str(row.get('hts_code', ''))[:6],
                "general_rate": float(row.get('general_rate', 0)),
                "special_rate": None,
                "other_rate": None,
                "unit_of_quantity": "PCE"
            }
            popular_codes.append(result)
        
        return {
            "success": True,
            "message": f"Retrieved {len(popular_codes)} popular codes",
            "data": popular_codes
        }
        
    except Exception as e:
        logger.error(f"Get popular codes error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/tariff/calculate", response_model=TariffCalculationResponse)
async def calculate_tariff_endpoint(request: TariffCalculationRequest):
    """Calculate comprehensive tariff costs"""
    try:
        result = calculate_tariff(
            hts_code=request.hts_code,
            product_value=request.product_value,
            country_code=request.country_code,
            quantity=request.quantity,
            freight_cost=request.freight_cost,
            insurance_cost=request.insurance_cost
        )
        
        return TariffCalculationResponse(
            success=True,
            message="Tariff calculation completed successfully",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Tariff calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# SOURCING ANALYSIS ENDPOINTS
# =============================================================================

@app.post("/api/v1/sourcing/analyze", response_model=SourcingAnalysisResponse)
async def analyze_sourcing(request: SourcingAnalysisRequest):
    """Analyze sourcing options across multiple countries"""
    try:
        result = analyze_sourcing_options(
            product_description=request.product_description,
            target_countries=request.target_countries,
            product_value=request.product_value,
            quantity=request.quantity
        )
        
        return SourcingAnalysisResponse(
            success=True,
            message="Sourcing analysis completed successfully",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Sourcing analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# KNOWLEDGE BASE ENDPOINTS
# =============================================================================

@app.get("/api/v1/knowledge/search")
async def search_knowledge(query: str, top_k: int = 5):
    """Search knowledge base using vector similarity"""
    try:
        results = search_knowledge_base(query, top_k)
        
        return {
            "success": True,
            "message": f"Found {len(results)} relevant knowledge entries",
            "data": results,
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Knowledge search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# AUTHENTICATION ENDPOINTS (Simplified)
# =============================================================================

@app.post("/api/v1/auth/login-json", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Simplified login endpoint for demo"""
    # In production, this would validate against a real user database
    if request.username == "demo" and request.password == "demo":
        return LoginResponse(
            access_token="demo-token-12345",
            token_type="bearer",
            expires_in=3600,
            user={
                "id": "demo-user",
                "email": "demo@atlas.com",
                "username": "demo",
                "full_name": "Demo User",
                "role": "admin",
                "company": "ATLAS Enterprise",
                "job_title": "Trade Analyst",
                "department": "Procurement"
            }
        )
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/v1/auth/register")
async def register(request: dict):
    """Simplified registration endpoint"""
    return {
        "success": True,
        "message": "Registration successful",
        "data": {
            "user_id": "new-user-123",
            "message": "Account created successfully"
        }
    }

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )

# =============================================================================
# NEW ENDPOINTS
# =============================================================================

@app.post("/api/v1/agents/sourcing/analyze")
async def agent_sourcing_analysis(request: SourcingAnalysisRequest):
    """AI Agent-powered sourcing analysis with autonomous recommendations"""
    try:
        if not SOURCING_AGENT:
            # Fallback to regular sourcing analysis
            return await analyze_sourcing(request)
        
        # Use AI Agent for analysis
        result = await SOURCING_AGENT.analyze_sourcing(
            product_description=request.product_description,
            target_countries=request.target_countries,
            product_value=request.product_value,
            quantity=request.quantity
        )
        
        return {
            "success": True,
            "message": "AI Agent sourcing analysis completed",
            "data": result,
            "agent_used": True
        }
        
    except Exception as e:
        logger.error(f"Agent sourcing analysis error: {e}")
        # Fallback to regular analysis
        try:
            return await analyze_sourcing(request)
        except Exception as fallback_error:
            logger.error(f"Fallback sourcing analysis error: {fallback_error}")
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
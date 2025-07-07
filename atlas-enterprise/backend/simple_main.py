"""
Simplified ATLAS Enterprise Backend
A minimal FastAPI application with essential endpoints for immediate functionality.
"""

import time
import os
import requests
import pandas as pd
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

# Global variable to store HTS data
HTS_DATA = None

def load_hts_data():
    """Load HTS data from Excel file"""
    global HTS_DATA
    try:
        # Load the Excel file
        excel_path = os.path.join(os.path.dirname(__file__), 'data', 'tariff_database_2025.xlsx')
        if os.path.exists(excel_path):
            df = pd.read_excel(excel_path)
            
            # Use the actual column names from the Excel file
            # Column 0: hts8 (HTS code)
            # Column 1: brief_description (product description)
            # Column 7: mfn_ad_val_rate this is the general tariff rate (tariff rate)
            
            # Rename columns for easier access
            df = df.rename(columns={
                df.columns[0]: 'hts_code',
                df.columns[1]: 'description',
                df.columns[7]: 'general_rate'
            })
            
            # Convert general_rate to numeric, handling any text values
            df['general_rate'] = pd.to_numeric(df['general_rate'], errors='coerce').fillna(0)
            
            logging.basicConfig(level=logging.INFO)
            logging.info('First 5 rows of loaded Excel data:')
            logging.info('\n' + df[['hts_code', 'description', 'general_rate']].head().to_string())
            
            # Convert to list of dictionaries for fast search
            HTS_DATA = df.to_dict('records')
            logging.info(f"Loaded {len(HTS_DATA)} HTS codes from Excel file")
            return True
        else:
            logging.error(f"Excel file not found at {excel_path}")
            return False
    except Exception as e:
        logging.error(f"Error loading HTS data: {e}")
        return False

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

# Simple models for API
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = 'groq'
    serp_search: Optional[bool] = False
    product_query: Optional[str] = None
    temperature: Optional[float] = 0.1
    max_tokens: Optional[int] = None

class ChatResponse(BaseModel):
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    product_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class HTSSearchRequest(BaseModel):
    query: str
    chapter: Optional[str] = None
    limit: int = 20

class HTSCode(BaseModel):
    id: int
    hts_code: str
    description: str
    general_rate: float
    special_rate: Optional[float]
    other_rate: Optional[float]
    unit_of_quantity: str
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

# Create FastAPI app
app = FastAPI(
    title="ATLAS Enterprise API",
    version="1.0.0",
    description="Simplified tariff management and trade intelligence platform"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load HTS data on startup
@app.on_event("startup")
async def startup_event():
    print("Loading HTS data...")
    load_hts_data()

# Mock data
MOCK_HTS_CODES = [
    {
        "id": 1,
        "hts_code": "8471.30.0100",
        "description": "Portable automatic data processing machines, weighing not more than 10 kg",
        "chapter": "84",
        "heading": "8471",
        "subheading": "8471.30",
        "general_rate": 0.0,
        "special_rate": None,
        "other_rate": None,
        "unit_of_quantity": "PCE"
    },
    {
        "id": 2,
        "hts_code": "8517.13.0000",
        "description": "Smartphones, cellular or other wireless networks",
        "chapter": "85",
        "heading": "8517",
        "subheading": "8517.13",
        "general_rate": 0.0,
        "special_rate": None,
        "other_rate": None,
        "unit_of_quantity": "PCE"
    },
    {
        "id": 3,
        "hts_code": "6104.43.2010",
        "description": "Women's dresses, of synthetic fibres, knitted or crocheted",
        "chapter": "61",
        "heading": "6104",
        "subheading": "6104.43",
        "general_rate": 16.0,
        "special_rate": None,
        "other_rate": None,
        "unit_of_quantity": "PCE"
    }
]

# Ollama integration
async def call_ollama(model: str, messages: List[Dict], temperature: float = 0.1, max_tokens: int = 1000):
    """Call local Ollama API"""
    try:
        # Format messages for Ollama
        formatted_messages = []
        
        # Add system message for ATLAS context
        formatted_messages.append({
            "role": "system",
            "content": """You are an expert AI assistant for ATLAS Enterprise, a tariff management and trade intelligence platform. You help users with:

- HTS code classification and analysis
- Tariff calculations and duty estimates  
- Trade compliance questions
- Sourcing optimization
- Regulatory guidance
- Import/export documentation

Provide accurate, helpful responses based on trade regulations and best practices."""
        })
        
        # Add user/assistant messages
        for message in messages:
            formatted_messages.append({
                "role": message["role"],
                "content": message["content"]
            })
        
        # Call Ollama API
        payload = {
            "model": model,
            "messages": formatted_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        response = requests.post(
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
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
            raise Exception(f"Ollama API error: {response.status_code}")
            
    except Exception as e:
        print(f"Ollama error: {e}")
        # Fallback response
        return {
            "content": f"I apologize, but I'm having trouble connecting to the {model} model right now. This could be because:\n\n1. The Ollama service isn't running\n2. The {model} model isn't available\n3. There's a temporary connection issue\n\nPlease ensure Ollama is running and the model is installed. You can check available models with: `ollama list`",
            "model": model,
            "usage": {"total_tokens": 0},
            "error": str(e)
        }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "ATLAS Enterprise API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "ai_chat": "/api/v1/ai/chat",
            "hts_search": "/api/v1/tariff/hts/search",
            "docs": "/docs"
        }
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "success": True,
        "message": "ATLAS Enterprise is healthy",
        "version": "1.0.0",
        "timestamp": time.time(),
        "checks": {
            "api": "healthy",
            "database": "bypassed",
            "ollama": "available" if check_ollama() else "unavailable"
        }
    }

def check_ollama():
    """Check if Ollama is available"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

# AI Chat endpoint
@app.post("/api/v1/ai/chat")
async def ai_chat(request: ChatRequest):
    """AI chat endpoint with Ollama integration"""
    try:
        # Check if it's a Groq model (not implemented yet)
        if request.model == 'groq':
            return ChatResponse(
                content="Groq integration is not yet implemented in this simplified version. Please use one of the local Ollama models instead.",
                model=request.model,
                error="Groq not implemented"
            )
        
        # Check if it's an OpenAI model (not implemented yet)
        if request.model == 'openai':
            return ChatResponse(
                content="OpenAI integration is not yet implemented in this simplified version. Please use one of the local Ollama models instead.",
                model=request.model,
                error="OpenAI not implemented"
            )
        
        # Use Ollama for local models
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        result = await call_ollama(
            model=request.model,
            messages=messages,
            temperature=request.temperature or 0.1,
            max_tokens=request.max_tokens or 1000
        )
        
        # Add product info if requested
        product_info = None
        if request.serp_search and request.product_query:
            product_info = {
                "note": "SerpAPI integration not implemented in simplified version",
                "query": request.product_query
            }
        
        return ChatResponse(
            content=result["content"],
            model=result["model"],
            usage=result.get("usage"),
            product_info=product_info,
            error=result.get("error")
        )
        
    except Exception as e:
        return ChatResponse(
            content="",
            model=request.model,
            error=str(e)
        )

# HTS Search endpoint
@app.get("/api/v1/tariff/hts/search")
async def search_hts(query: str, chapter: Optional[str] = None, limit: int = 20):
    """Search HTS codes using real Excel data"""
    try:
        start_time = time.time()
        
        # Use real HTS data if available, otherwise fall back to mock data
        if HTS_DATA:
            results = search_hts_data(query, chapter, limit)
        else:
            # Fallback to mock data if Excel file not loaded
            filtered_codes = []
            for code in MOCK_HTS_CODES:
                if (query.lower() in code["description"].lower() or 
                    query in code["hts_code"] or
                    (chapter and code["chapter"] == chapter)):
                    filtered_codes.append(code)
            results = filtered_codes[:limit]
        
        search_time = int((time.time() - start_time) * 1000)
        
        return HTSSearchResponse(
            success=True,
            message=f"Found {len(results)} HTS codes",
            data=results,
            total_results=len(results),
            search_query=query,
            search_time_ms=search_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get specific HTS code
@app.get("/api/v1/tariff/hts/{hts_code}")
async def get_hts_code(hts_code: str):
    """Get specific HTS code"""
    try:
        for code in MOCK_HTS_CODES:
            if code["hts_code"] == hts_code:
                return {
                    "success": True,
                    "message": f"HTS code found: {hts_code}",
                    "data": code
                }
        
        raise HTTPException(status_code=404, detail=f"HTS code not found: {hts_code}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chapters endpoint
@app.get("/api/v1/tariff/chapters")
async def get_chapters():
    """Get HTS chapters"""
    chapters = [
        {"chapter_number": "84", "description": "Nuclear reactors, boilers, machinery", "code_count": 150},
        {"chapter_number": "85", "description": "Electrical machinery and equipment", "code_count": 120},
        {"chapter_number": "61", "description": "Articles of apparel, knitted or crocheted", "code_count": 80}
    ]
    
    return {
        "success": True,
        "message": f"Retrieved {len(chapters)} HTS chapters",
        "data": chapters
    }

# Popular codes endpoint
@app.get("/api/v1/tariff/popular-codes")
async def get_popular_codes(limit: int = 10):
    """Get popular HTS codes"""
    return {
        "success": True,
        "message": f"Retrieved {min(limit, len(MOCK_HTS_CODES))} popular codes",
        "data": MOCK_HTS_CODES[:limit]
    }

# Tariff calculation endpoint
@app.post("/api/v1/tariff/calculate")
async def calculate_tariff(request: dict):
    """Calculate tariff costs"""
    try:
        hts_code = request.get("hts_code", "")
        product_value = float(request.get("product_value", 0))
        
        # Mock calculation
        duty_rate = 15.0  # 15% duty rate
        duty_amount = product_value * (duty_rate / 100)
        mpf_amount = product_value * 0.003464  # MPF rate
        hmf_amount = product_value * 0.00125   # HMF rate
        total_landed_cost = product_value + duty_amount + mpf_amount + hmf_amount
        
        return {
            "success": True,
            "message": "Calculation completed successfully",
            "data": {
                "hts_code": hts_code,
                "product_value_usd": product_value,
                "duty_rate": duty_rate,
                "duty_amount": duty_amount,
                "mpf_amount": mpf_amount,
                "hmf_amount": hmf_amount,
                "total_landed_cost": total_landed_cost,
                "calculation_breakdown": {
                    "product_value": product_value,
                    "duty_calculation": f"{duty_rate}% of ${product_value:,.2f}",
                    "mpf_calculation": f"0.3464% of ${product_value:,.2f}",
                    "hmf_calculation": f"0.125% of ${product_value:,.2f}"
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Auth endpoints (simplified)
@app.post("/api/v1/auth/login-json")
async def login(request: dict):
    """Simplified login endpoint"""
    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "access_token": "demo-token",
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {
                "id": "demo",
                "email": "demo@atlas.com",
                "username": "demo",
                "full_name": "Demo User",
                "role": "user"
            }
        }
    }

@app.post("/api/v1/auth/register")
async def register(request: dict):
    """Simplified register endpoint"""
    return {
        "success": True,
        "message": "Registration successful",
        "data": {
            "access_token": "demo-token",
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {
                "id": "demo",
                "email": request.get("email", "demo@atlas.com"),
                "username": request.get("username", "demo"),
                "full_name": f"{request.get('first_name', 'Demo')} {request.get('last_name', 'User')}",
                "role": "user"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
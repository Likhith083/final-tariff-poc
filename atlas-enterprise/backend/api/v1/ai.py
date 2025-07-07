from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from services.groq_service import groq_service
from services.ollama_service import ollama_service
# from services.openai_service import openai_service  # Placeholder for future
# from services.serp_service import serp_service      # Placeholder for future

router = APIRouter(prefix="/ai", tags=["ai"])

class ChatMessage(BaseModel):
    role: Literal['user', 'assistant']
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = Field('groq', description="LLM model to use")
    serp_search: Optional[bool] = Field(False, description="Whether to trigger SerpAPI product search")
    product_query: Optional[str] = Field(None, description="Product search query for SerpAPI")
    temperature: Optional[float] = 0.1
    max_tokens: Optional[int] = None

class ChatResponse(BaseModel):
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    product_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Unified AI chat endpoint supporting Groq, OpenAI, Ollama, and optional SerpAPI product search.
    """
    try:
        # 1. LLM response
        if request.model == 'groq':
            llm_result = await groq_service.chat_completion(
                messages=[m.model_dump() for m in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
        elif request.model == 'openai':
            # llm_result = await openai_service.chat_completion(...)
            raise HTTPException(status_code=501, detail="OpenAI integration not yet implemented.")
        elif request.model in ['llava', 'devstral:24b', 'llama3.2:3b', 'qwen3:8b', 'deepseek-r1:8b', 'moondream', 'llama3.1', 'gemma3:4b', 'phi4']:
            # Use Ollama with knowledge base integration
            llm_result = await ollama_service.chat_with_knowledge_base(
                model=request.model,
                messages=[m.model_dump() for m in request.messages],
                query=request.messages[-1].content if request.messages else "",
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
        else:
            raise HTTPException(status_code=400, detail=f"Invalid model specified: {request.model}")

        # 2. SerpAPI product info (if requested)
        product_info = None
        if request.serp_search and request.product_query:
            # product_info = await serp_service.search_product(request.product_query)
            product_info = {"title": "Mock product", "price": "$99", "source": "serpapi"}

        return ChatResponse(
            content=llm_result["content"],
            model=llm_result.get("model", request.model),
            usage=llm_result.get("usage"),
            product_info=product_info
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        return ChatResponse(content="", model=request.model, error=str(e)) 
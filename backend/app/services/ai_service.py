import httpx
import json
import re
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.services.vector_store import VectorStoreService

class TariffManagementAI:
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.vector_store = VectorStoreService()
        
    async def get_response(self, message: str, session_id: Optional[int] = None) -> str:
        """
        Main entry point for Tariff Management Chatbot
        Handles all functional requirements from SRS
        """
        try:
            # Parse user intent and extract relevant information
            intent = self._parse_user_intent(message)
            
            # Route to appropriate handler based on intent
            if intent["type"] == "tariff_calculation":
                return await self._handle_tariff_calculation(intent, message)
            elif intent["type"] == "product_search":
                return await self._handle_product_search(intent, message)
            elif intent["type"] == "material_suggestions":
                return await self._handle_material_suggestions(intent, message)
            elif intent["type"] == "what_if_scenario":
                return await self._handle_what_if_scenario(intent, message)
            elif intent["type"] == "hts_lookup":
                return await self._handle_hts_lookup(intent, message)
            elif intent["type"] == "sourcing_alternatives":
                return await self._handle_sourcing_alternatives(intent, message)
            else:
                return await self._handle_general_query(message)
                
        except Exception as e:
            print(f"Tariff AI Error: {str(e)}")
            return "I'm experiencing technical difficulties. Please try rephrasing your tariff-related question."
    
    def _parse_user_intent(self, message: str) -> Dict[str, Any]:
        """Parse user message to determine intent and extract entities"""
        msg_lower = message.lower()
        
        # Extract HTS/HS codes
        hts_pattern = r'\b(\d{4}[\.\d]*)\b'
        hts_codes = re.findall(hts_pattern, message)
        
        # Extract countries
        countries = self._extract_countries(message)
        
        # Extract product names and companies
        product_info = self._extract_product_info(message)
        
        # Determine intent based on keywords
        if any(keyword in msg_lower for keyword in ['tariff for', 'duty for', 'cost of importing', 'calculate tariff']):
            return {
                "type": "tariff_calculation",
                "hts_codes": hts_codes,
                "countries": countries,
                "products": product_info["products"],
                "companies": product_info["companies"]
            }
        elif any(keyword in msg_lower for keyword in ['what if', 'scenario', 'sourcing from', 'change country']):
            return {
                "type": "what_if_scenario",
                "hts_codes": hts_codes,
                "countries": countries,
                "products": product_info["products"]
            }
        elif any(keyword in msg_lower for keyword in ['material alternative', 'reduce tariff', 'cheaper material', 'composition']):
            return {
                "type": "material_suggestions", 
                "hts_codes": hts_codes,
                "products": product_info["products"]
            }
        elif any(keyword in msg_lower for keyword in ['hts code', 'hs code', 'classification', 'classify']):
            return {
                "type": "hts_lookup",
                "products": product_info["products"]
            }
        elif any(keyword in msg_lower for keyword in ['alternative sourcing', 'other countries', 'cheaper countries']):
            return {
                "type": "sourcing_alternatives",
                "hts_codes": hts_codes,
                "products": product_info["products"],
                "current_country": countries[0] if countries else None
            }
        elif any(keyword in msg_lower for keyword in ['search', 'find product', 'company']):
            return {
                "type": "product_search",
                "products": product_info["products"],
                "companies": product_info["companies"]
            }
        else:
            return {
                "type": "general",
                "entities": {
                    "hts_codes": hts_codes,
                    "countries": countries,
                    "products": product_info["products"],
                    "companies": product_info["companies"]
                }
            }
    
    def _extract_countries(self, message: str) -> List[str]:
        """Extract country names from message"""
        countries = [
            "china", "mexico", "vietnam", "thailand", "malaysia", "india", 
            "taiwan", "south korea", "japan", "germany", "italy", "canada",
            "united states", "usa", "brazil", "argentina", "chile"
        ]
        
        found_countries = []
        msg_lower = message.lower()
        for country in countries:
            if country in msg_lower:
                found_countries.append(country.title())
        
        return found_countries
    
    def _extract_product_info(self, message: str) -> Dict[str, List[str]]:
        """Extract product names and company names from message"""
        # Common company indicators
        company_indicators = ["mckesson", "stanley black & decker", "sbd", "3m", "honeywell", "dupont"]
        
        # Common products
        product_indicators = [
            "gloves", "nitrile gloves", "medical gloves", "drill", "cordless drill",
            "screwdriver", "hammer", "wrench", "mask", "respirator", "safety equipment"
        ]
        
        msg_lower = message.lower()
        
        companies = []
        for company in company_indicators:
            if company in msg_lower:
                companies.append(company.title())
        
        products = []
        for product in product_indicators:
            if product in msg_lower:
                products.append(product.title())
        
        return {"products": products, "companies": companies}

    async def _handle_tariff_calculation(self, intent: Dict[str, Any], message: str) -> str:
        """Handle tariff calculation requests (FR-01)"""
        try:
            # Get relevant tariff information from knowledge base
            search_query = f"tariff calculation {' '.join(intent.get('products', []))} {' '.join(intent.get('countries', []))}"
            relevant_docs = await self.vector_store.search_knowledge(search_query, n_results=1)
            
            # Extract HTS codes and countries
            hts_codes = intent.get("hts_codes", [])
            countries = intent.get("countries", [])
            products = intent.get("products", [])
            
            # Build context for AI
            context = self._format_context_docs(relevant_docs)
            
            prompt = f"""You are a Tariff Management AI assistant. Calculate tariff and landed costs based on this request:

User Query: {message}

Available Information:
- HTS Codes: {hts_codes if hts_codes else 'Not specified'}
- Countries: {countries if countries else 'Not specified'}
- Products: {products if products else 'Not specified'}

Knowledge Base Context:
{context}

Based on the SRS requirements, provide a detailed tariff calculation including:
1. Product identification and material composition
2. Appropriate HTS code (if not provided, suggest one)
3. Tariff rate from current data
4. Calculation breakdown (base price → tariff → MPF → total landed cost)
5. Data source references

Format your response professionally like the SRS examples, including specific dollar amounts and percentages.
If information is missing, ask the user to provide it (e.g., base price, country of origin)."""

            return await self._generate_ai_response(prompt)
            
        except Exception as e:
            return f"Error processing tariff calculation: {str(e)}. Please provide HTS code, product description, and country of origin."

    async def _handle_product_search(self, intent: Dict[str, Any], message: str) -> str:
        """Handle product detail search and HTS code inference (FR-02)"""
        try:
            products = intent.get("products", [])
            companies = intent.get("companies", [])
            
            # Search knowledge base for product information
            search_query = f"product {' '.join(products)} {' '.join(companies)} HTS classification"
            relevant_docs = await self.vector_store.search_knowledge(search_query, n_results=1)
            
            context = self._format_context_docs(relevant_docs)
            
            prompt = f"""You are a Tariff Management AI assistant specializing in product classification and HTS code inference.

User Query: {message}

Product Information:
- Products: {products if products else 'Not specified'}
- Companies: {companies if companies else 'Not specified'}

Knowledge Base Context:
{context}

Following SRS requirements (FR-02), provide:
1. Product identification and material composition inference
2. Appropriate HTS code classification (6-10 digits)
3. Tariff rate for the classified product
4. Justification for the classification
5. Data source references

Format like the SRS examples (e.g., McKesson nitrile gloves scenario).
If you need more information, ask for product description or company name."""

            return await self._generate_ai_response(prompt)
            
        except Exception as e:
            return f"Error processing product search: {str(e)}. Please provide a product description and optionally a company name."

    async def _handle_material_suggestions(self, intent: Dict[str, Any], message: str) -> str:
        """Handle material proportion suggestions (FR-03)"""
        try:
            products = intent.get("products", [])
            hts_codes = intent.get("hts_codes", [])
            
            # Search for material alternatives in knowledge base
            search_query = f"material composition alternatives {' '.join(products)} tariff reduction"
            relevant_docs = await self.vector_store.search_knowledge(search_query, n_results=3)
            
            context = self._format_context_docs(relevant_docs)
            
            prompt = f"""You are a Tariff Management AI assistant specializing in material optimization for tariff reduction.

User Query: {message}

Available Information:
- Products: {products if products else 'Not specified'}
- HTS Codes: {hts_codes if hts_codes else 'Not specified'}

Knowledge Base Context:
{context}

Following SRS requirements (FR-03), provide material proportion suggestions:
1. Current material composition analysis
2. Alternative material compositions with lower tariff rates
3. Estimated tariff savings per unit
4. Quality impact assessment (keep <10% impact)
5. HTS codes for alternative materials

Format like the SRS cordless drill example showing percentage changes and cost savings.
Suggest 2-3 alternative compositions."""

            return await self._generate_ai_response(prompt)
            
        except Exception as e:
            return f"Error processing material suggestions: {str(e)}. Please provide product description or HTS code."

    async def _handle_what_if_scenario(self, intent: Dict[str, Any], message: str) -> str:
        """Handle what-if scenario simulation (FR-04)"""
        try:
            countries = intent.get("countries", [])
            hts_codes = intent.get("hts_codes", [])
            products = intent.get("products", [])
            
            # Search for scenario-related information
            search_query = f"tariff rates comparison {' '.join(countries)} {' '.join(products)}"
            relevant_docs = await self.vector_store.search_knowledge(search_query, n_results=3)
            
            context = self._format_context_docs(relevant_docs)
            
            prompt = f"""You are a Tariff Management AI assistant specializing in what-if scenario analysis.

User Query: {message}

Scenario Parameters:
- Countries: {countries if countries else 'Not specified'}
- HTS Codes: {hts_codes if hts_codes else 'Not specified'}
- Products: {products if products else 'Not specified'}

Knowledge Base Context:
{context}

Following SRS requirements (FR-04), provide scenario simulation:
1. Current scenario costs (original country/tariff)
2. Alternative scenario costs (new country/tariff)
3. Comparative cost summary showing savings/increases
4. FTA benefits where applicable
5. Recommendations based on analysis

Format as a clear before/after comparison with specific dollar amounts and percentages.
Consider trade agreements and their benefits."""

            return await self._generate_ai_response(prompt)
            
        except Exception as e:
            return f"Error processing scenario simulation: {str(e)}. Please specify current and target countries or tariff rates."

    async def _handle_hts_lookup(self, intent: Dict[str, Any], message: str) -> str:
        """Handle HTS code lookup and classification (FR-05)"""
        try:
            products = intent.get("products", [])
            
            # Search knowledge base for HTS classification information
            search_query = f"HTS classification {' '.join(products)} harmonized tariff schedule"
            relevant_docs = await self.vector_store.search_knowledge(search_query, n_results=5)
            
            context = self._format_context_docs(relevant_docs)
            
            prompt = f"""You are a Tariff Management AI assistant specializing in HTS code classification.

User Query: {message}

Products for Classification: {products if products else 'Extract from query'}

Knowledge Base Context:
{context}

Following SRS requirements (FR-05), provide HTS lookup:
1. Suggested HTS codes (up to 5 options with confidence levels)
2. Tariff rates for each suggested code
3. Classification justification
4. Reference links to USITC/WCO schedules
5. Match confidence (aim for >80%)

Format with clear HTS code suggestions and explanations.
If the query contains an HTS code, provide the corresponding tariff rate and classification details."""

            return await self._generate_ai_response(prompt)
            
        except Exception as e:
            return f"Error processing HTS lookup: {str(e)}. Please provide a product description or HTS code."

    async def _handle_sourcing_alternatives(self, intent: Dict[str, Any], message: str) -> str:
        """Handle alternative sourcing suggestions (FR-06)"""
        try:
            hts_codes = intent.get("hts_codes", [])
            current_country = intent.get("current_country")
            products = intent.get("products", [])
            
            # Search for sourcing alternatives
            search_query = f"alternative sourcing countries tariff rates {' '.join(products)} FTA benefits"
            relevant_docs = await self.vector_store.search_knowledge(search_query, n_results=1)
            
            context = self._format_context_docs(relevant_docs)
            
            prompt = f"""You are a Tariff Management AI assistant specializing in alternative sourcing recommendations.

User Query: {message}

Sourcing Parameters:
- Current Country: {current_country if current_country else 'Not specified'}
- HTS Codes: {hts_codes if hts_codes else 'Not specified'}
- Products: {products if products else 'Not specified'}

Knowledge Base Context:
{context}

Following SRS requirements (FR-06), provide sourcing alternatives:
1. Ranked list of 3-5 alternative countries
2. Tariff rates for each country
3. Potential savings compared to current sourcing
4. FTA benefits (USMCA, etc.)
5. Total landed cost comparison

Format like the SRS drill example showing country options with specific savings.
Prioritize countries with lowest total landed costs."""

            return await self._generate_ai_response(prompt)
            
        except Exception as e:
            return f"Error processing sourcing alternatives: {str(e)}. Please provide current country and product/HTS code."

    async def _handle_general_query(self, message: str) -> str:
        """Handle general tariff-related queries"""
        try:
            # Search knowledge base for general tariff information
            relevant_docs = await self.vector_store.search_knowledge(message, n_results=1)
            
            context = self._format_context_docs(relevant_docs)
            
            prompt = f"""You are a Tariff Management AI assistant helping with trade, customs, and tariff questions.

User Query: {message}

Knowledge Base Context:
{context}

Provide helpful information about the user's tariff-related question. Include:
1. Direct answer to their question
2. Relevant background information
3. Actionable next steps or recommendations
4. References to official sources when appropriate

Keep responses professional and focused on practical trade/customs guidance."""

            return await self._generate_ai_response(prompt)
            
        except Exception as e:
            return f"I'm experiencing technical difficulties. Please try rephrasing your question or ask about specific tariff calculations, HTS codes, or sourcing alternatives."

    def _format_context_docs(self, relevant_docs: List[Dict[str, Any]]) -> str:
        """Format retrieved documents into context string"""
        if not relevant_docs:
            return "No specific information found in knowledge base."
        
        context_parts = []
        for i, doc in enumerate(relevant_docs, 1):
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            source = metadata.get('source', 'knowledge_base')
            category = metadata.get('category', 'general')
            
            context_parts.append(f"Reference {i} (Source: {source}, Category: {category}):\n{content}")
        
        return "\n\n".join(context_parts)
    
    async def _generate_ai_response(self, prompt: str) -> str:
        """Generate AI response using Ollama"""
        try:
            print(f"DEBUG: Attempting to connect to Ollama at {self.base_url}")
            print(f"DEBUG: Using model: {self.model}")
            
            # Optimize prompt length to reduce processing time
            optimized_prompt = self._optimize_prompt(prompt)
            print(f"DEBUG: Optimized prompt length: {len(optimized_prompt)} chars")
            
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": optimized_prompt}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.2,  # Lower for more consistent responses
                        "top_p": 0.9,
                        "num_predict": 600,  # Reduced for faster responses
                        "num_ctx": 2048,     # Context window optimization
                        "repeat_penalty": 1.1
                    }
                }
                print(f"DEBUG: Request payload: {payload}")
                
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=120.0  # Increased timeout for slow responses
                )
                
                print(f"DEBUG: Response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"DEBUG: Response result: {result}")
                    return self._extract_response_content(result)
                else:
                    print(f"DEBUG: Error response: {response.text}")
                    return "I'm currently experiencing technical difficulties with the AI service. Please try again in a moment."
                    
        except Exception as e:
            print(f"DEBUG: Exception in _generate_ai_response: {str(e)}")
            print(f"DEBUG: Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            return "I'm currently unable to access the AI service. Please try again later."
    
    def _optimize_prompt(self, prompt: str) -> str:
        """Optimize prompt length and structure for faster responses"""
        # If prompt is too long, truncate context while keeping the core request
        max_length = 2000  # Reduced from potentially very long prompts
        
        if len(prompt) <= max_length:
            return prompt
        
        # Split prompt into sections
        lines = prompt.split('\n')
        
        # Keep the first part (usually the role/instruction)
        result_lines = []
        current_length = 0
        
        for line in lines:
            if current_length + len(line) > max_length:
                # If we're in context section, add a truncation note
                if "Knowledge Base Context:" in '\n'.join(result_lines[-3:]):
                    result_lines.append("... (context truncated for performance) ...")
                break
            result_lines.append(line)
            current_length += len(line) + 1  # +1 for newline
        
        return '\n'.join(result_lines)

    def _extract_response_content(self, result: Dict[str, Any]) -> str:
        """Extract response content from Ollama API response"""
        if 'message' in result and isinstance(result['message'], dict):
            return result['message'].get('content', "I apologize, but I couldn't generate a response at this time.")
        elif 'message' in result:
            return result['message']
        elif 'response' in result:
            return result['response']
        else:
            return "I apologize, but I couldn't generate a response at this time."
    
    async def classify_product(self, description: str) -> Dict[str, Any]:
        """Classify a product and suggest HTS codes (legacy method for compatibility)"""
        try:
            # Use the new HTS lookup handler
            intent = {"type": "hts_lookup", "products": [description]}
            response = await self._handle_hts_lookup(intent, f"Classify product: {description}")
            
            # Try to extract structured data for backward compatibility
            return {
                "hts_code": "See response for suggestions",
                "explanation": response,
                "duty_rate_range": "See response for rates",
                "considerations": "Refer to detailed response"
            }
        except Exception as e:
            return {
                "hts_code": "Unknown",
                "explanation": f"Error: {str(e)}",
                "duty_rate_range": "Unknown",
                "considerations": "Please try again or consult official HTS resources"
            }
    
    async def explain_duty_calculation(self, hts_code: str, duty_rate: float, value: float) -> str:
        """Explain duty calculation (legacy method for compatibility)"""
        try:
            message = f"Explain duty calculation for HTS {hts_code}, duty rate {duty_rate}%, value ${value}"
            intent = {"type": "tariff_calculation", "hts_codes": [hts_code]}
            return await self._handle_tariff_calculation(intent, message)
        except Exception as e:
            return f"Error explaining duty calculation: {str(e)}"

# Keep the class name as AIService for backward compatibility
AIService = TariffManagementAI

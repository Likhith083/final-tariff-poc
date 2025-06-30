import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz, process
import requests
from forex_python.converter import CurrencyRates
import sqlite3
from pathlib import Path
import zipfile
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import threading
import time
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Tariff Management Chatbot", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
tariff_data = None
embedding_model = None
currency_converter = None
llm_client = None
chroma_client = None
chroma_collection = None
alert_subscriptions = {}
user_sessions = {}

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class HTSearchRequest(BaseModel):
    query: str
    limit: int = 10

class TariffCalculationRequest(BaseModel):
    hts_code: str
    material_cost: float
    country_of_origin: str
    shipping_cost: float = 0.0
    currency: str = "USD"

class ProductSearchRequest(BaseModel):
    product_description: str
    company_name: Optional[str] = None
    country_of_origin: str = "China"

class MaterialSuggestionRequest(BaseModel):
    hts_code: str
    current_materials: Dict[str, float]
    quality_priority: str = "balanced"  # cost, quality, balanced

class ScenarioRequest(BaseModel):
    hts_code: str
    material_cost: float
    current_country: str
    new_country: Optional[str] = None
    new_tariff_rate: Optional[float] = None

class AlertSubscription(BaseModel):
    hts_codes: List[str]
    email: str
    frequency: str = "daily"  # daily, weekly, monthly

class ReportRequest(BaseModel):
    hts_codes: List[str]
    suppliers: List[str]
    regions: List[str]
    time_period: str = "1y"
    format: str = "csv"  # csv, pdf, json

class CurrencyConversionRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str

class DataIngestionRequest(BaseModel):
    hts_code: str
    description: str
    tariff_rate: float
    country: str = "US"

# Initialize LLM client
def initialize_llm():
    global llm_client
    try:
        # Test Ollama connection
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            if any('llama3.2:3b' in model.get('name', '') for model in models):
                llm_client = "http://localhost:11434"
                logger.info("LLM (llama3.2:3b) is available")
            else:
                logger.warning("llama3.2:3b model not found in Ollama")
                llm_client = None
        else:
            logger.warning("Ollama not available")
            llm_client = None
    except Exception as e:
        logger.warning(f"LLM not available: {e}")
        llm_client = None

# Initialize embedding model
def initialize_embedding_model():
    global embedding_model
    try:
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Embedding model initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing embedding model: {e}")
        embedding_model = None

# Initialize ChromaDB
def initialize_chroma():
    global chroma_client, chroma_collection
    try:
        chroma_client = chromadb.PersistentClient(path="./data/chroma")
        collection_name = "hts_search"
        
        try:
            chroma_collection = chroma_client.get_collection(name=collection_name)
            logger.info(f"Loading existing collection: {collection_name}")
        except:
            logger.info(f"Creating new collection: {collection_name}")
            chroma_collection = chroma_client.create_collection(name=collection_name)
            
        # Index tariff data if collection is empty
        if chroma_collection.count() == 0 and tariff_data is not None:
            index_tariff_data()
            
        logger.info("ChromaDB collection 'hts_search' ready")
    except Exception as e:
        logger.error(f"Error initializing ChromaDB: {e}")
        chroma_collection = None

def index_tariff_data():
    """Index tariff data in ChromaDB for vector search"""
    global chroma_collection, tariff_data
    
    if tariff_data is None or chroma_collection is None:
        return
        
    try:
        # Prepare data for indexing
        documents = []
        metadatas = []
        ids = []
        
        for idx, row in tariff_data.iterrows():
            hts_code = str(row.get('hts8', '')).strip()
            description = str(row.get('brief_description', '')).strip()
            
            if hts_code and hts_code != 'nan' and description and description != 'nan':
                # Create document text
                doc_text = f"HTS Code: {hts_code}. Description: {description}"
                
                documents.append(doc_text)
                metadatas.append({
                    "hts_code": hts_code,
                    "description": description,
                    "tariff_rate": float(row.get('mfn_ad_val_rate this is the general tariff rate', 0)),
                    "specific_rate": float(row.get('mfn_specific_rate', 0)),
                    "other_rate": float(row.get('mfn_other_rate', 0))
                })
                ids.append(f"doc_{idx}")
        
        # Add documents in batches
        batch_size = 1000
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            chroma_collection.add(
                documents=documents[i:end_idx],
                metadatas=metadatas[i:end_idx],
                ids=ids[i:end_idx]
            )
            
        logger.info(f"Added {len(documents)} documents to ChromaDB collection")
        
    except Exception as e:
        logger.error(f"Error indexing tariff data: {e}")

# Initialize currency converter
def initialize_currency_converter():
    global currency_converter
    try:
        currency_converter = CurrencyRates()
        logger.info("Currency converter initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing currency converter: {e}")
        currency_converter = None

# Load and index tariff data
def load_tariff_data():
    global tariff_data
    
    try:
        excel_file = "data/tariff_database_2025.xlsx"
        if os.path.exists(excel_file):
            tariff_data = pd.read_excel(excel_file)
            logger.info(f"Loaded Excel data: {len(tariff_data)} rows, {len(tariff_data.columns)} columns")
            logger.info(f"Columns: {list(tariff_data.columns)}")
        else:
            logger.error(f"Excel file not found: {excel_file}")
            # Create sample data for testing
            create_sample_data()
            
    except Exception as e:
        logger.error(f"Error loading tariff data: {e}")
        create_sample_data()

def create_sample_data():
    """Create sample tariff data for testing"""
    global tariff_data
    
    sample_data = {
        'hts8': ['6104.43.00', '7304.41.00', '8471.30.01', '8517.13.00', '9503.00.00'],
        'brief_description': [
            'Women\'s cotton t-shirts',
            'Steel pipes and tubes, seamless, of circular cross-section, of stainless steel',
            'Laptop computers',
            'Smartphones',
            'Toys and games'
        ],
        'mfn_ad_val_rate this is the general tariff rate': [16.0, 2.5, 0.0, 0.0, 0.0],
        'mfn_specific_rate': [0.0, 0.0, 0.0, 0.0, 0.0],
        'mfn_other_rate': [0.0, 0.0, 0.0, 0.0, 0.0]
    }
    
    tariff_data = pd.DataFrame(sample_data)

# Simple and effective HTS search - works like Excel Ctrl+F
def search_hts_codes(query: str, limit: int = 10) -> List[Dict]:
    """Simple text-based HTS search - fast and reliable like Excel Ctrl+F"""
    results = []
    query_lower = query.lower().strip()
    
    if tariff_data is None:
        logger.error("Tariff data not loaded")
        return results
    
    logger.info(f"Searching for: '{query}' in {len(tariff_data)} records")
    
    for idx, row in tariff_data.iterrows():
        try:
            hts_code = str(row.get('hts8', '')).strip()
            description = str(row.get('brief_description', '')).strip()
            
            # Skip empty or invalid entries
            if not hts_code or hts_code == 'nan' or not description or description == 'nan':
                continue
            
            # Check if query appears in HTS code or description
            hts_lower = hts_code.lower()
            desc_lower = description.lower()
            
            # Calculate match score
            score = 0
            
            # Exact HTS code match gets highest score
            if query_lower == hts_lower:
                score = 100
            # Partial HTS code match (query is part of HTS code)
            elif query_lower in hts_lower:
                score = 90
            # Query appears in description (exact word match) - most important for "steel"
            elif query_lower in desc_lower:
                # Count how many times the query appears
                occurrences = desc_lower.count(query_lower)
                score = 80 + (occurrences * 5)  # More occurrences = higher score
            # Word boundary match (query is a complete word in description)
            elif f" {query_lower} " in f" {desc_lower} " or desc_lower.startswith(query_lower + " ") or desc_lower.endswith(" " + query_lower):
                score = 75
            # Only use fuzzy matching for longer queries (5+ characters) and very high threshold
            elif len(query_lower) >= 5:
                # Use fuzzy matching for similar terms with very high threshold
                hts_fuzzy = fuzz.partial_ratio(query_lower, hts_lower)
                desc_fuzzy = fuzz.partial_ratio(query_lower, desc_lower)
                score = max(hts_fuzzy, desc_fuzzy)
                # Only include if fuzzy match is very good (85%+)
                if score < 85:
                    score = 0
            
            # Only include results with very high match confidence
            if score >= 75:  # Much higher threshold to avoid false matches
                # Improved tariff rate extraction with better error handling
                tariff_rate = 0.0
                specific_rate = 0.0
                
                try:
                    # Try to get tariff rate with better error handling
                    rate_value = row.get('mfn_ad_val_rate this is the general tariff rate')
                    if rate_value is not None and str(rate_value).strip() != 'nan':
                        tariff_rate = float(rate_value)
                        logger.info(f"Found tariff rate for {hts_code}: {tariff_rate}")
                    else:
                        logger.warning(f"No valid tariff rate found for {hts_code}, value: {rate_value}")
                    
                    specific_value = row.get('mfn_specific_rate')
                    if specific_value is not None and str(specific_value).strip() != 'nan':
                        specific_rate = float(specific_value)
                        
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing tariff rates for {hts_code}: {e}")
                    tariff_rate = 0.0
                    specific_rate = 0.0
                
                result = {
                    'hts_code': hts_code,
                    'description': description,
                    'mfn_rate': tariff_rate,
                    'specific_rate': specific_rate,
                    'other_rate': float(row.get('mfn_other_rate', 0)),
                    'similarity_score': score,
                    'index': idx
                }
                results.append(result)
                
        except Exception as e:
            logger.warning(f"Error processing row {idx}: {e}")
            continue
    
    # Sort by similarity score (highest first)
    results.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    logger.info(f"Found {len(results)} results for query '{query}'")
    return results[:limit]

def fallback_text_search(query: str, limit: int) -> List[Dict]:
    """Fallback text-based search when vector search fails"""
    return search_hts_codes(query, limit)

# Tariff calculation functions
def calculate_tariff(hts_code: str, material_cost: float, country: str, shipping_cost: float = 0.0) -> Dict:
    """Calculate tariff and landed cost"""
    try:
        # Find tariff rate
        tariff_rate = 0.0
        specific_rate = 0.0
        
        if tariff_data is not None:
            # Search for exact HTS code match
            matches = tariff_data[tariff_data['hts8'] == hts_code]
            if not matches.empty:
                row = matches.iloc[0]
                
                # Improved tariff rate extraction with better error handling
                try:
                    rate_value = row.get('mfn_ad_val_rate this is the general tariff rate')
                    if rate_value is not None and str(rate_value).strip() != 'nan':
                        tariff_rate = float(rate_value)
                        logger.info(f"Found tariff rate for {hts_code}: {tariff_rate}")
                    else:
                        logger.warning(f"No valid tariff rate found for {hts_code}, value: {rate_value}")
                    
                    specific_value = row.get('mfn_specific_rate')
                    if specific_value is not None and str(specific_value).strip() != 'nan':
                        specific_rate = float(specific_value)
                        
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing tariff rates for {hts_code}: {e}")
                    tariff_rate = 0.0
                    specific_rate = 0.0
            else:
                logger.warning(f"No HTS code match found for: {hts_code}")
        
        # Calculate costs
        ad_valorem_tariff = material_cost * (tariff_rate / 100)
        specific_tariff = specific_rate
        total_tariff = ad_valorem_tariff + specific_tariff
        
        # MPF (Merchandise Processing Fee) - typically 0.3464% of value
        mpf = (material_cost + total_tariff) * 0.003464
        
        # Total landed cost
        landed_cost = material_cost + total_tariff + mpf + shipping_cost
        
        return {
            'hts_code': hts_code,
            'material_cost': material_cost,
            'tariff_rate': tariff_rate,
            'specific_rate': specific_rate,
            'ad_valorem_tariff': ad_valorem_tariff,
            'specific_tariff': specific_tariff,
            'total_tariff': total_tariff,
            'mpf': mpf,
            'shipping_cost': shipping_cost,
            'landed_cost': landed_cost,
            'country': country
        }
        
    except Exception as e:
        logger.error(f"Error calculating tariff: {e}")
        return {
            'error': f"Error calculating tariff: {str(e)}",
            'hts_code': hts_code,
            'material_cost': material_cost,
            'landed_cost': material_cost
        }

# Product search and material inference
def search_product_details(product_description: str, company_name: str = None) -> Dict:
    """Search product details and infer material composition"""
    try:
        # Enhanced search query
        search_terms = [product_description]
        if company_name:
            search_terms.append(company_name)
        
        # Material inference based on keywords
        materials = infer_materials(product_description)
        
        # Find best HTS code match
        hts_results = search_hts_codes(product_description, limit=5)
        best_match = hts_results[0] if hts_results else None
        
        return {
            'product_description': product_description,
            'company_name': company_name,
            'inferred_materials': materials,
            'suggested_hts_code': best_match['hts_code'] if best_match else None,
            'tariff_rate': best_match['mfn_rate'] if best_match else 0,
            'confidence': best_match['similarity_score'] if best_match else 0,
            'alternative_hts_codes': [r['hts_code'] for r in hts_results[1:3]]
        }
        
    except Exception as e:
        logger.error(f"Error searching product details: {e}")
        return {
            'error': f"Error searching product details: {str(e)}",
            'product_description': product_description
        }

def infer_materials(description: str) -> Dict[str, float]:
    """Infer material composition from product description"""
    description_lower = description.lower()
    materials = {}
    
    # Material keywords and their typical percentages
    material_keywords = {
        'cotton': 100,
        'polyester': 100,
        'wool': 100,
        'silk': 100,
        'nylon': 100,
        'steel': 100,
        'aluminum': 100,
        'plastic': 100,
        'wood': 100,
        'leather': 100,
        'rubber': 100,
        'glass': 100,
        'ceramic': 100
    }
    
    # Check for material keywords
    for material, default_percentage in material_keywords.items():
        if material in description_lower:
            materials[material] = default_percentage
    
    # If no materials found, make educated guess
    if not materials:
        if any(word in description_lower for word in ['shirt', 'dress', 'fabric', 'cloth']):
            materials['cotton'] = 100
        elif any(word in description_lower for word in ['pipe', 'tube', 'metal', 'iron']):
            materials['steel'] = 100
        elif any(word in description_lower for word in ['phone', 'computer', 'electronic']):
            materials['plastic'] = 70
            materials['metal'] = 30
    
    return materials

# Material proportion suggestions
def suggest_material_alternatives(hts_code: str, current_materials: Dict[str, float], quality_priority: str = "balanced") -> List[Dict]:
    """Suggest alternative material compositions to reduce tariffs"""
    try:
        suggestions = []
        
        # Get current tariff rate
        current_rate = 0.0
        if tariff_data is not None:
            matches = tariff_data[tariff_data['hts8'] == hts_code]
            if not matches.empty:
                current_rate = float(matches.iloc[0].get('mfn_ad_val_rate this is the general tariff rate', 0))
        
        # Material alternatives based on priority
        alternatives = {
            'cost': [
                {'material': 'polyester', 'percentage': 100, 'cost_reduction': 0.3},
                {'material': 'plastic', 'percentage': 100, 'cost_reduction': 0.4},
                {'material': 'aluminum', 'percentage': 100, 'cost_reduction': 0.2}
            ],
            'quality': [
                {'material': 'silk', 'percentage': 100, 'quality_improvement': 0.5},
                {'material': 'leather', 'percentage': 100, 'quality_improvement': 0.4},
                {'material': 'steel', 'percentage': 100, 'quality_improvement': 0.3}
            ],
            'balanced': [
                {'material': 'cotton', 'percentage': 100, 'balance_score': 0.8},
                {'material': 'nylon', 'percentage': 100, 'balance_score': 0.7},
                {'material': 'wood', 'percentage': 100, 'balance_score': 0.6}
            ]
        }
        
        for alt in alternatives.get(quality_priority, alternatives['balanced']):
            suggestion = {
                'hts_code': hts_code,
                'current_materials': current_materials,
                'suggested_materials': {alt['material']: alt['percentage']},
                'priority': quality_priority,
                'current_tariff_rate': current_rate,
                'estimated_impact': alt.get('cost_reduction', alt.get('quality_improvement', alt.get('balance_score', 0))),
                'reasoning': f"Switching to {alt['material']} for {quality_priority} optimization"
            }
            suggestions.append(suggestion)
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error suggesting material alternatives: {e}")
        return []

# What-if scenario simulation
def simulate_scenario(hts_code: str, material_cost: float, current_country: str, 
                     new_country: str = None, new_tariff_rate: float = None) -> Dict:
    """Simulate what-if scenarios for tariff changes"""
    try:
        # Get current scenario
        current_scenario = calculate_tariff(hts_code, material_cost, current_country)
        
        # Calculate new scenario
        new_scenario = current_scenario.copy()
        if new_country:
            new_scenario['country'] = new_country
        if new_tariff_rate is not None:
            new_scenario['tariff_rate'] = new_tariff_rate
            new_scenario['ad_valorem_tariff'] = material_cost * (new_tariff_rate / 100)
            new_scenario['total_tariff'] = new_scenario['ad_valorem_tariff'] + new_scenario['specific_tariff']
            new_scenario['landed_cost'] = material_cost + new_scenario['total_tariff'] + new_scenario['mpf'] + new_scenario['shipping_cost']
        
        # Calculate impact
        cost_difference = new_scenario['landed_cost'] - current_scenario['landed_cost']
        percentage_change = (cost_difference / current_scenario['landed_cost']) * 100 if current_scenario['landed_cost'] > 0 else 0
        
        return {
            'hts_code': hts_code,
            'current_scenario': current_scenario,
            'new_scenario': new_scenario,
            'impact_analysis': {
                'cost_difference': cost_difference,
                'percentage_change': percentage_change,
                'savings' if cost_difference < 0 else 'additional_cost': abs(cost_difference)
            }
        }
        
    except Exception as e:
        logger.error(f"Error simulating scenario: {e}")
        return {
            'error': f"Error simulating scenario: {str(e)}",
            'hts_code': hts_code
        }

# Alternative sourcing suggestions
def suggest_alternative_sources(hts_code: str, current_country: str) -> List[Dict]:
    """Suggest alternative sourcing countries"""
    try:
        suggestions = []
        
        # Common alternative countries with their typical tariff rates
        alternative_countries = {
            'Mexico': {'tariff_rate': 0.0, 'shipping_cost': 500, 'lead_time': 7},
            'Canada': {'tariff_rate': 0.0, 'shipping_cost': 800, 'lead_time': 10},
            'Vietnam': {'tariff_rate': 5.0, 'shipping_cost': 1200, 'lead_time': 21},
            'India': {'tariff_rate': 7.5, 'shipping_cost': 1500, 'lead_time': 25},
            'Thailand': {'tariff_rate': 4.0, 'shipping_cost': 1300, 'lead_time': 18}
        }
        
        # Get current country info
        current_info = alternative_countries.get(current_country, {'tariff_rate': 10.0, 'shipping_cost': 1000, 'lead_time': 15})
        
        for country, info in alternative_countries.items():
            if country != current_country:
                # Calculate cost comparison
                current_total = current_info['shipping_cost'] + (current_info['tariff_rate'] / 100 * 10000)  # Assuming $10k material cost
                new_total = info['shipping_cost'] + (info['tariff_rate'] / 100 * 10000)
                savings = current_total - new_total
                
                suggestion = {
                    'country': country,
                    'tariff_rate': info['tariff_rate'],
                    'shipping_cost': info['shipping_cost'],
                    'lead_time_days': info['lead_time'],
                    'estimated_savings': savings,
                    'recommendation': 'Recommended' if savings > 0 else 'Consider'
                }
                suggestions.append(suggestion)
        
        # Sort by savings
        suggestions.sort(key=lambda x: x['estimated_savings'], reverse=True)
        return suggestions
        
    except Exception as e:
        logger.error(f"Error suggesting alternative sources: {e}")
        return []

# Alert subscription management
def subscribe_to_alerts(hts_codes: List[str], email: str, frequency: str = "daily") -> Dict:
    """Subscribe to tariff change alerts"""
    try:
        subscription_id = f"{email}_{int(time.time())}"
        
        alert_subscriptions[subscription_id] = {
            'hts_codes': hts_codes,
            'email': email,
            'frequency': frequency,
            'created_at': datetime.now(),
            'last_alert': None
        }
        
        return {
            'subscription_id': subscription_id,
            'hts_codes': hts_codes,
            'email': email,
            'frequency': frequency,
            'status': 'active',
            'message': f"Successfully subscribed to alerts for {len(hts_codes)} HTS codes"
        }
        
    except Exception as e:
        logger.error(f"Error subscribing to alerts: {e}")
        return {
            'error': f"Error subscribing to alerts: {str(e)}"
        }

def send_alert_email(email: str, hts_code: str, old_rate: float, new_rate: float):
    """Send alert email for tariff changes"""
    try:
        # This would integrate with your email service
        logger.info(f"Alert email sent to {email} for HTS {hts_code}: {old_rate}% -> {new_rate}%")
    except Exception as e:
        logger.error(f"Error sending alert email: {e}")

# Report generation
def generate_report(hts_codes: List[str], suppliers: List[str], regions: List[str], 
                   time_period: str = "1y", format: str = "csv") -> Dict:
    """Generate comprehensive tariff reports"""
    try:
        report_data = {
            'hts_codes': hts_codes,
            'suppliers': suppliers,
            'regions': regions,
            'time_period': time_period,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_hts_codes': len(hts_codes),
                'total_suppliers': len(suppliers),
                'total_regions': len(regions)
            }
        }
        
        # Add tariff data for each HTS code
        tariff_summary = []
        if tariff_data is not None:
            for hts_code in hts_codes:
                matches = tariff_data[tariff_data['hts8'] == hts_code]
                if not matches.empty:
                    row = matches.iloc[0]
                    tariff_summary.append({
                        'hts_code': hts_code,
                        'description': str(row.get('brief_description', '')),
                        'mfn_rate': float(row.get('mfn_ad_val_rate this is the general tariff rate', 0)),
                        'specific_rate': float(row.get('mfn_specific_rate', 0))
                    })
        
        report_data['tariff_summary'] = tariff_summary
        
        return {
            'report_id': f"report_{int(time.time())}",
            'format': format,
            'data': report_data,
            'download_url': f"/api/reports/download/{int(time.time())}"
        }
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return {
            'error': f"Error generating report: {str(e)}"
        }

# Visualization creation
def create_visualization(hts_codes: List[str], regions: List[str]) -> str:
    """Create tariff visualization charts"""
    try:
        # Create sample visualization data
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Sample data for demonstration
        hts_labels = hts_codes[:5] if len(hts_codes) > 5 else hts_codes
        tariff_rates = [5.0, 10.0, 15.0, 2.5, 0.0][:len(hts_labels)]
        
        # Bar chart
        ax1.bar(hts_labels, tariff_rates, color='skyblue')
        ax1.set_title('Tariff Rates by HTS Code')
        ax1.set_ylabel('Tariff Rate (%)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Pie chart for regions
        region_data = [30, 25, 20, 15, 10][:len(regions)]
        ax2.pie(region_data, labels=regions, autopct='%1.1f%%')
        ax2.set_title('Import Distribution by Region')
        
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
        
    except Exception as e:
        logger.error(f"Error creating visualization: {e}")
        return ""

# Currency conversion function
def convert_currency(amount: float, from_currency: str, to_currency: str) -> Dict:
    """Convert currency using forex-python"""
    try:
        if currency_converter is None:
            return {"error": "Currency converter not available"}
        
        # Get current exchange rate
        rate = currency_converter.get_rate(from_currency.upper(), to_currency.upper())
        converted_amount = amount * rate
        
        return {
            "original_amount": amount,
            "original_currency": from_currency.upper(),
            "converted_amount": round(converted_amount, 2),
            "target_currency": to_currency.upper(),
            "exchange_rate": round(rate, 4),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Currency conversion error: {e}")
        return {"error": f"Currency conversion failed: {str(e)}"}

# Enhanced AI chat with LLM integration
def process_chat_message(message: str, session_id: str = None) -> str:
    """Process chat message with LLM integration"""
    try:
        # Initialize session if needed
        if session_id not in user_sessions:
            user_sessions[session_id] = {
                "history": [],
                "context": "You are a helpful tariff and trade assistant. You help users with HTS codes, tariff calculations, trade scenarios, and international commerce questions."
            }
        
        # Add message to history
        user_sessions[session_id]["history"].append({"role": "user", "content": message})
        
        # Try LLM first if available
        if llm_client:
            try:
                llm_response = query_llm(message, session_id)
                if llm_response:
                    user_sessions[session_id]["history"].append({"role": "assistant", "content": llm_response})
                    return llm_response
            except Exception as e:
                logger.error(f"LLM query failed: {e}")
        
        # Fallback to rule-based responses
        response = handle_chat_fallback(message, session_id)
        user_sessions[session_id]["history"].append({"role": "assistant", "content": response})
        return response
        
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        return "I'm sorry, I encountered an error processing your message. Please try again."

def query_llm(message: str, session_id: str) -> str:
    """Query the LLM for enhanced responses"""
    try:
        if llm_client is None:
            return None
            
        # Prepare context from session history
        context = user_sessions[session_id]["context"]
        history = user_sessions[session_id]["history"][-5:]  # Last 5 messages for context
        
        # Build prompt
        prompt = f"{context}\n\n"
        for msg in history:
            prompt += f"{msg['role'].title()}: {msg['content']}\n"
        prompt += "Assistant: "
        
        # Query Ollama
        response = requests.post(
            f"{llm_client}/api/generate",
            json={
                "model": "llama3.2:3b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '').strip()
        else:
            logger.error(f"LLM API error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error querying LLM: {e}")
        return None

def handle_chat_fallback(message: str, session_id: str) -> str:
    """Fallback chat handler when LLM is not available"""
    message_lower = message.lower()
    
    # Check for specific query types
    if any(word in message_lower for word in ['hts', 'code', 'tariff', 'classification']):
        return handle_tariff_query(message, session_id)
    elif any(word in message_lower for word in ['search', 'find', 'lookup']):
        return handle_search_query(message, session_id)
    elif any(word in message_lower for word in ['material', 'component', 'ingredient']):
        return handle_material_query(message, session_id)
    elif any(word in message_lower for word in ['scenario', 'what if', 'compare']):
        return handle_scenario_query(message, session_id)
    elif any(word in message_lower for word in ['source', 'supplier', 'country']):
        return handle_sourcing_query(message, session_id)
    elif any(word in message_lower for word in ['alert', 'notification', 'monitor']):
        return handle_alert_query(message, session_id)
    elif any(word in message_lower for word in ['report', 'analysis', 'data']):
        return handle_report_query(message, session_id)
    else:
        return handle_general_query(message, session_id)

def handle_tariff_query(message: str, session_id: str) -> str:
    """Handle tariff-related queries"""
    return """I can help you with tariff calculations and information. Here are some things I can do:

1. **Calculate tariffs** - Provide HTS code and material cost
2. **Search HTS codes** - Find the right classification for your product
3. **Compare rates** - See how tariffs vary by country
4. **Scenario analysis** - What-if calculations for different scenarios

What specific tariff information do you need?"""

def handle_search_query(message: str, session_id: str) -> str:
    """Handle HTS search queries"""
    return """I can help you search for HTS codes. Here's how to use the search:

1. **Product description** - "cotton t-shirts", "steel pipes", "electronic components"
2. **HTS code** - "6104.43.00", "7304.41.00"
3. **Material-based** - "cotton", "steel", "plastic"

The search uses advanced vector similarity to find the most relevant codes. What product are you looking for?"""

def handle_material_query(message: str, session_id: str) -> str:
    """Handle material-related queries"""
    return """I can help with material analysis and suggestions:

1. **Material inference** - Automatically detect materials from product descriptions
2. **Alternative suggestions** - Find cost-effective material substitutions
3. **Composition optimization** - Balance cost vs quality

What material information do you need?"""

def handle_scenario_query(message: str, session_id: str) -> str:
    """Handle scenario simulation queries"""
    return """I can help you simulate different scenarios:

1. **Country changes** - Compare tariffs across different countries
2. **Rate changes** - What if tariff rates change?
3. **Cost impact** - Calculate total landed cost differences
4. **Savings analysis** - Identify potential cost savings

What scenario would you like to analyze?"""

def handle_sourcing_query(message: str, session_id: str) -> str:
    """Handle sourcing-related queries"""
    return """I can help you find alternative sourcing options:

1. **Country alternatives** - Compare different sourcing countries
2. **Cost comparison** - Total cost including tariffs and shipping
3. **Lead time analysis** - Consider delivery time impacts
4. **Risk assessment** - Evaluate sourcing risks

What sourcing information do you need?"""

def handle_alert_query(message: str, session_id: str) -> str:
    """Handle alert-related queries"""
    return """I can help you set up tariff change alerts:

1. **HTS code monitoring** - Get notified when rates change
2. **Email notifications** - Daily, weekly, or monthly updates
3. **Custom thresholds** - Alert when changes exceed certain amounts
4. **Multiple codes** - Monitor several products at once

Would you like to set up alerts for specific HTS codes?"""

def handle_report_query(message: str, session_id: str) -> str:
    """Handle report-related queries"""
    return """I can generate comprehensive reports:

1. **Tariff summaries** - Overview of rates for multiple products
2. **Cost analysis** - Detailed cost breakdowns
3. **Trend analysis** - Historical rate changes
4. **Export options** - CSV, PDF, or JSON formats

What type of report would you like to generate?"""

def handle_general_query(message: str, session_id: str) -> str:
    """Handle general queries"""
    return """Welcome to the Tariff Management Assistant! I can help you with:

🔍 **HTS Code Search** - Find the right classification for your products
💰 **Tariff Calculations** - Calculate duties and total landed costs
🌍 **Sourcing Analysis** - Compare costs across different countries
📊 **Reports & Analytics** - Generate comprehensive tariff reports
🔔 **Alerts & Monitoring** - Stay updated on tariff changes
📈 **Scenario Planning** - What-if analysis for different situations
💱 **Currency Conversion** - Real-time exchange rates
📝 **Data Ingestion** - Add new HTS codes and descriptions

What would you like to work on today?"""

# Data ingestion function
def ingest_hts_data(hts_code: str, description: str, tariff_rate: float, country: str = "US") -> Dict:
    """Ingest new HTS data into the system"""
    try:
        global tariff_data
        
        # Create new row
        new_row = {
            'hts8': hts_code,
            'brief_description': description,
            'mfn_ad_val_rate this is the general tariff rate': tariff_rate,
            'mfn_specific_rate': 0.0,
            'mfn_other_rate': 0.0
        }
        
        # Add to tariff data
        if tariff_data is not None:
            tariff_data = pd.concat([tariff_data, pd.DataFrame([new_row])], ignore_index=True)
            
            # Update ChromaDB if available
            if chroma_collection is not None:
                doc_text = f"HTS Code: {hts_code}. Description: {description}"
                chroma_collection.add(
                    documents=[doc_text],
                    metadatas=[{
                        "hts_code": hts_code,
                        "description": description,
                        "tariff_rate": tariff_rate,
                        "specific_rate": 0.0,
                        "other_rate": 0.0
                    }],
                    ids=[f"manual_{datetime.now().timestamp()}"]
                )
        
        logger.info(f"Added manual HTS entry: {hts_code} - {description}")
        
        return {
            "success": True,
            "message": f"Successfully added HTS code {hts_code}",
            "hts_code": hts_code,
            "description": description,
            "tariff_rate": tariff_rate
        }
        
    except Exception as e:
        logger.error(f"Error ingesting HTS data: {e}")
        return {"error": f"Failed to ingest data: {str(e)}"}

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "vector_store": False,
            "embedding_model": embedding_model is not None,
            "tariff_data": tariff_data is not None,
            "currency_converter": currency_converter is not None
        },
        "data_stats": {
            "total_records": len(tariff_data) if tariff_data is not None else 0,
            "vector_documents": 0
        }
    }

@app.post("/api/chat")
async def chat_endpoint(request: ChatMessage):
    """Enhanced chat endpoint with LLM integration"""
    try:
        # Generate session ID if not provided
        if not request.session_id:
            request.session_id = f"session_{int(time.time())}"
        
        response = process_chat_message(request.message, request.session_id)
        
        return {
            "response": response,
            "session_id": request.session_id,
            "timestamp": datetime.now().isoformat(),
            "llm_available": llm_client is not None
        }
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Chat processing failed")

@app.post("/api/hts/search")
async def hts_search_endpoint(request: HTSearchRequest):
    """HTS code search endpoint"""
    try:
        results = search_hts_codes(request.query, request.limit)
        return {
            "query": request.query,
            "results": results,
            "total_found": len(results),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in HTS search endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tariff/calculate")
async def tariff_calculation_endpoint(request: TariffCalculationRequest):
    """Tariff calculation endpoint"""
    try:
        result = calculate_tariff(
            request.hts_code,
            request.material_cost,
            request.country_of_origin,
            request.shipping_cost
        )
        return result
    except Exception as e:
        logger.error(f"Error in tariff calculation endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/product/search")
async def product_search_endpoint(request: ProductSearchRequest):
    """Product search and material inference endpoint"""
    try:
        result = search_product_details(
            request.product_description,
            request.company_name
        )
        return result
    except Exception as e:
        logger.error(f"Error in product search endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/materials/suggest")
async def material_suggestion_endpoint(request: MaterialSuggestionRequest):
    """Material alternative suggestions endpoint"""
    try:
        suggestions = suggest_material_alternatives(
            request.hts_code,
            request.current_materials,
            request.quality_priority
        )
        return {
            "hts_code": request.hts_code,
            "current_materials": request.current_materials,
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Error in material suggestion endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scenario/simulate")
async def scenario_simulation_endpoint(request: ScenarioRequest):
    """What-if scenario simulation endpoint"""
    try:
        result = simulate_scenario(
            request.hts_code,
            request.material_cost,
            request.current_country,
            request.new_country,
            request.new_tariff_rate
        )
        return result
    except Exception as e:
        logger.error(f"Error in scenario simulation endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sourcing/suggest")
async def sourcing_suggestion_endpoint(request: dict):
    """Alternative sourcing suggestions endpoint"""
    try:
        hts_code = request.get('hts_code')
        current_country = request.get('current_country', 'China')
        
        if not hts_code:
            raise HTTPException(status_code=400, detail="hts_code is required")
        
        suggestions = suggest_alternative_sources(hts_code, current_country)
        return {
            "hts_code": hts_code,
            "current_country": current_country,
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Error in sourcing suggestion endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/alerts/subscribe")
async def alert_subscription_endpoint(request: AlertSubscription):
    """Alert subscription endpoint"""
    try:
        result = subscribe_to_alerts(
            request.hts_codes,
            request.email,
            request.frequency
        )
        return result
    except Exception as e:
        logger.error(f"Error in alert subscription endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reports/generate")
async def report_generation_endpoint(request: ReportRequest):
    """Report generation endpoint"""
    try:
        result = generate_report(
            request.hts_codes,
            request.suppliers,
            request.regions,
            request.time_period,
            request.format
        )
        return result
    except Exception as e:
        logger.error(f"Error in report generation endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/visualization/create")
async def visualization_endpoint(request: dict):
    """Create tariff visualization endpoint"""
    try:
        hts_codes = request.get('hts_codes', [])
        regions = request.get('regions', ['China', 'Mexico', 'Canada'])
        
        if not hts_codes:
            raise HTTPException(status_code=400, detail="hts_codes is required")
        
        image_base64 = create_visualization(hts_codes, regions)
        
        return {
            "visualization": image_base64,
            "format": "base64_png",
            "hts_codes": hts_codes,
            "regions": regions
        }
    except Exception as e:
        logger.error(f"Error in visualization endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hts/codes")
async def get_hts_codes(limit: int = 10):
    """Get sample HTS codes"""
    try:
        if tariff_data is not None:
            sample_codes = tariff_data.head(limit)[['hts8', 'brief_description']].to_dict('records')
            return {
                "hts_codes": sample_codes,
                "total_available": len(tariff_data)
            }
        else:
            return {"hts_codes": [], "total_available": 0}
    except Exception as e:
        logger.error(f"Error getting HTS codes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/currency/convert")
async def currency_conversion_endpoint(request: CurrencyConversionRequest):
    """Convert currency using real-time exchange rates"""
    result = convert_currency(request.amount, request.from_currency, request.to_currency)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/api/data/ingest")
async def data_ingestion_endpoint(request: DataIngestionRequest):
    """Ingest new HTS data into the system"""
    result = ingest_hts_data(request.hts_code, request.description, request.tariff_rate, request.country)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# Static file serving
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def read_root():
    """Serve the main HTML file"""
    return FileResponse("index.html")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting Tariff Management Chatbot...")
    
    # Initialize embedding model
    initialize_embedding_model()
    
    # Load tariff data
    load_tariff_data()
    
    # Initialize ChromaDB
    initialize_chroma()
    
    # Initialize LLM
    initialize_llm()
    
    # Initialize currency converter
    initialize_currency_converter()
    
    logger.info("Application startup complete!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 
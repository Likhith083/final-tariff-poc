from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class HTSCode(Base):
    """HTS Code model"""
    __tablename__ = "hts_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    hts_code = Column(String(20), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    tariff_rate = Column(Float, nullable=False)
    country_origin = Column(String(50), nullable=False)
    effective_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ChatSession(Base):
    """Chat session model"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(String(50), nullable=True)  # For future user authentication
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationship
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    """Chat message model"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("chat_sessions.session_id"), nullable=False)
    message_type = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    message_metadata = Column(JSON, nullable=True)  # Store additional info like confidence, sources
    
    # Relationship
    session = relationship("ChatSession", back_populates="messages")

class TariffCalculation(Base):
    """Tariff calculation history"""
    __tablename__ = "tariff_calculations"
    
    id = Column(Integer, primary_key=True, index=True)
    hts_code = Column(String(20), nullable=False)
    country_origin = Column(String(50), nullable=False)
    material_cost = Column(Float, nullable=False)
    tariff_rate = Column(Float, nullable=False)
    tariff_amount = Column(Float, nullable=False)
    total_landed_cost = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    calculated_at = Column(DateTime, default=func.now())
    user_id = Column(String(50), nullable=True)

class MaterialAnalysis(Base):
    """Material analysis history"""
    __tablename__ = "material_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    original_composition = Column(JSON, nullable=False)
    suggested_composition = Column(JSON, nullable=False)
    cost_savings = Column(Float, nullable=False)
    quality_impact = Column(String(100), nullable=False)
    recommendations = Column(JSON, nullable=False)
    analyzed_at = Column(DateTime, default=func.now())
    user_id = Column(String(50), nullable=True)

class Scenario(Base):
    """Scenario simulation history"""
    __tablename__ = "scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    base_scenario = Column(JSON, nullable=False)
    modified_scenario = Column(JSON, nullable=False)
    savings = Column(Float, nullable=False)
    percentage_change = Column(Float, nullable=False)
    risk_assessment = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    user_id = Column(String(50), nullable=True)

class Report(Base):
    """Report generation history"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(50), unique=True, index=True, nullable=False)
    report_type = Column(String(50), nullable=False)
    parameters = Column(JSON, nullable=True)
    file_path = Column(String(255), nullable=True)
    generated_at = Column(DateTime, default=func.now())
    user_id = Column(String(50), nullable=True)

class DataIngestion(Base):
    """Data ingestion history"""
    __tablename__ = "data_ingestions"
    
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    records_processed = Column(Integer, nullable=False)
    records_added = Column(Integer, nullable=False)
    records_updated = Column(Integer, nullable=False)
    errors = Column(JSON, nullable=True)
    ingested_at = Column(DateTime, default=func.now())
    user_id = Column(String(50), nullable=True)

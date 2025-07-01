"""
Database configuration and models
"""
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from .config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


class HTSCode(Base):
    """HTS Code model"""
    __tablename__ = "hts_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    chapter = Column(String(2))
    heading = Column(String(4))
    subheading = Column(String(4))
    statistical_suffix = Column(String(2))
    level = Column(Integer)
    parent_code = Column(String(10))
    tariff_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Country(Base):
    """Country model"""
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    iso_code = Column(String(2), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class TariffRate(Base):
    """Tariff Rate model"""
    __tablename__ = "tariff_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    hts_code_id = Column(Integer, ForeignKey("hts_codes.id"), nullable=False)
    country_of_origin_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    country_of_import_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    effective_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime)
    rate_percentage = Column(Float)
    rate_amount = Column(Float)
    currency = Column(String(3), default="USD")
    type = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    hts_code = relationship("HTSCode")
    country_of_origin = relationship("Country", foreign_keys=[country_of_origin_id])
    country_of_import = relationship("Country", foreign_keys=[country_of_import_id])


class Product(Base):
    """Product model"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    material_composition_text = Column(Text)
    inferred_material_composition = Column(Text)  # JSON string
    current_hts_code_id = Column(Integer, ForeignKey("hts_codes.id"))
    company_name = Column(String(255))
    source_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    hts_code = relationship("HTSCode")


class Material(Base):
    """Material model"""
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    properties_json = Column(Text)  # JSON string
    hts_code_id_suggestion = Column(Integer, ForeignKey("hts_codes.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    hts_code = relationship("HTSCode")


class ChatSession(Base):
    """Chat Session model"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatMessage(Base):
    """Chat Message model"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.session_id"), nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    metadata = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)


class AlertSubscription(Base):
    """Alert Subscription model"""
    __tablename__ = "alert_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    hts_code_id = Column(Integer, ForeignKey("hts_codes.id"), nullable=False)
    country_of_origin_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    country_of_import_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    email = Column(String(255), nullable=False)
    notification_frequency = Column(String(20), default="daily")
    last_notified_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    hts_code = relationship("HTSCode")
    country_of_origin = relationship("Country", foreign_keys=[country_of_origin_id])
    country_of_import = relationship("Country", foreign_keys=[country_of_import_id])


# Database dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database dependency for FastAPI"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Database initialization
async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created successfully")


# Insert sample data
async def insert_sample_data():
    """Insert sample data for development"""
    async with AsyncSessionLocal() as session:
        # Check if data already exists
        existing_countries = await session.execute(
            "SELECT COUNT(*) FROM countries"
        )
        if existing_countries.scalar() > 0:
            print("✅ Sample data already exists")
            return
        
        # Insert sample countries
        countries = [
            Country(name="United States", iso_code="US"),
            Country(name="China", iso_code="CN"),
            Country(name="Canada", iso_code="CA"),
            Country(name="Mexico", iso_code="MX"),
            Country(name="Germany", iso_code="DE"),
            Country(name="Japan", iso_code="JP"),
            Country(name="United Kingdom", iso_code="GB"),
            Country(name="France", iso_code="FR"),
            Country(name="Italy", iso_code="IT"),
            Country(name="South Korea", iso_code="KR"),
        ]
        
        session.add_all(countries)
        await session.commit()
        
        # Insert sample HTS codes
        hts_codes = [
            HTSCode(
                code="8471.30.01",
                description="Portable automatic data processing machines",
                chapter="84",
                heading="8471",
                subheading="30",
                level=4,
                tariff_rate=0.0
            ),
            HTSCode(
                code="8517.13.00",
                description="Smartphones",
                chapter="85",
                heading="8517",
                subheading="13",
                level=4,
                tariff_rate=0.0
            ),
            HTSCode(
                code="9503.00.00",
                description="Other toys",
                chapter="95",
                heading="9503",
                subheading="00",
                level=4,
                tariff_rate=0.0
            ),
            HTSCode(
                code="6104.43.20",
                description="Women's dresses of synthetic fibers",
                chapter="61",
                heading="6104",
                subheading="43",
                level=4,
                tariff_rate=16.0
            ),
            HTSCode(
                code="8528.72.72",
                description="Color television receivers",
                chapter="85",
                heading="8528",
                subheading="72",
                level=4,
                tariff_rate=5.0
            ),
        ]
        
        session.add_all(hts_codes)
        await session.commit()
        
        print("✅ Sample data inserted successfully") 
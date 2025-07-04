from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class HTSRecord(Base):
    __tablename__ = "hts_records"
    
    id = Column(Integer, primary_key=True, index=True)
    hts_code = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    duty_rate = Column(Float)
    category = Column(String)
    subcategory = Column(String)
    notes = Column(Text)
    effective_date = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 
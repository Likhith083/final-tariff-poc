from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class TariffCalculation(Base):
    __tablename__ = "tariff_calculations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    hts_code = Column(String, nullable=False)
    description = Column(Text)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    duty_rate = Column(Float, nullable=False)
    duty_amount = Column(Float, nullable=False)
    total_with_duty = Column(Float, nullable=False)
    calculation_details = Column(JSON)  # Store additional calculation parameters
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User") 
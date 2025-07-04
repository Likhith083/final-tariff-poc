from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base
import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    company = Column(String)
    material_composition = Column(JSON)
    hts_code = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Tariff(Base):
    __tablename__ = 'tariffs'
    id = Column(Integer, primary_key=True, index=True)
    hts_code = Column(String, index=True)
    country = Column(String, index=True)
    rate = Column(Float)
    effective_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    hts_code = Column(String, index=True)
    email = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship('User')

class Scenario(Base):
    __tablename__ = 'scenarios'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship('User')

class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship('User') 
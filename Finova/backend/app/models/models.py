from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database.db import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    filename = Column(String)
    expense_data = Column(JSON)
    cfo_analysis = Column(Text)
    trends = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InvestmentScenario(Base):
    __tablename__ = "investment_scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, index=True)
    scenario_number = Column(Integer)
    title = Column(String)
    description = Column(Text)
    expected_return = Column(Float)
    risk_level = Column(String)
    details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

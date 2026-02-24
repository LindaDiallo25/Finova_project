from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Analysis schemas
class ExpenseData(BaseModel):
    category: str
    amount: float
    date: str


class AnalysisCreate(BaseModel):
    filename: str
    expense_data: List[Dict[str, Any]]


class CFOAnalysisResponse(BaseModel):
    summary: str
    trends: List[str]
    recommendations: List[str]
    total_expenses: float
    average_daily_expense: float


class AnalysisResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    cfo_analysis: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Investment scenario schemas
class InvestmentScenarioData(BaseModel):
    scenario_number: int
    title: str
    description: str
    expected_return: float
    risk_level: str
    details: Dict[str, Any]


class InvestmentScenarioResponse(BaseModel):
    id: int
    analysis_id: int
    scenario_number: int
    title: str
    description: str
    expected_return: float
    risk_level: str
    details: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


class StrategistResponse(BaseModel):
    analysis_id: int
    scenarios: List[InvestmentScenarioResponse]
    market_comparison: Dict[str, Any]

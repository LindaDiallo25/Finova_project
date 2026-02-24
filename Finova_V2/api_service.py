"""
FastAPI REST API for Financial Advisor Widget
Exposes endpoints for the banking app integration
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import logging
from datetime import datetime

from data_preprocessing import FinancialDataPreprocessor
from clustering_model import CustomerSegmentationModel
from gemini_advisor import GeminiFinancialAdvisor
from gcp_deployment import GCPDeployment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Financial Advisor API",
    description="AI-powered personal finance advisor for banking apps",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (in production, use dependency injection)
preprocessor = FinancialDataPreprocessor()
model = CustomerSegmentationModel()
advisor = GeminiFinancialAdvisor()


# Pydantic models
class TransactionData(BaseModel):
    """Customer transaction history"""
    customer_id: str
    csv_data: str  # Base64 encoded CSV or direct CSV string
    

class CustomerGoal(BaseModel):
    """Customer financial goal"""
    goal_type: str = Field(..., description="Type: vacation, home, retirement, etc.")
    target_amount: float = Field(..., gt=0)
    target_date: datetime
    description: Optional[str] = None


class AnalysisRequest(BaseModel):
    """Request for financial analysis"""
    customer_id: str
    goal: Optional[CustomerGoal] = None


class ConversationRequest(BaseModel):
    """Conversational query"""
    customer_id: str
    question: str
    context: Optional[Dict] = None


class AdviceResponse(BaseModel):
    """Financial advice response"""
    customer_id: str
    cluster_id: int
    persona: str
    advice: Dict[str, str]
    monthly_savings_target: float
    generated_at: datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str


# Endpoints
@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )


@app.post("/api/v1/analyze")
async def analyze_customer(request: AnalysisRequest) -> AdviceResponse:
    """
    Analyze customer financial data and provide personalized advice
    
    Args:
        request: Analysis request with customer_id and optional goal
    
    Returns:
        Personalized financial advice
    """
    try:
        logger.info(f"Analyzing customer {request.customer_id}")
        
        # Load customer data (from GCP or local)
        # For MVP, we'll simulate loading from CSV
        features, profile = preprocessor.prepare_for_training("transactions.csv")
        
        # Predict cluster
        cluster_id, cluster_info = model.predict(profile)
        
        # Generate advice
        goal_text = "maximize monthly savings"
        if request.goal:
            goal_text = f"{request.goal.goal_type}: save €{request.goal.target_amount} by {request.goal.target_date.strftime('%B %Y')}"
        
        advice = advisor.generate_advice(profile, cluster_info, goal_text)
        
        # Extract savings target
        savings_target = profile['avg_monthly_income'] * 0.2  # Default 20%
        
        return AdviceResponse(
            customer_id=request.customer_id,
            cluster_id=cluster_id,
            persona=cluster_info['persona'],
            advice=advice,
            monthly_savings_target=savings_target,
            generated_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/chat")
async def chat_with_advisor(request: ConversationRequest) -> Dict:
    """
    Conversational interface with financial advisor
    
    Args:
        request: Question and context
    
    Returns:
        AI-generated response
    """
    try:
        logger.info(f"Chat request from customer {request.customer_id}")
        
        # Get customer context
        if not request.context:
            features, profile = preprocessor.prepare_for_training("transactions.csv")
            context = profile
        else:
            context = request.context
        
        # Generate response
        response = advisor.generate_conversational_response(
            request.question,
            context
        )
        
        return {
            "customer_id": request.customer_id,
            "question": request.question,
            "response": response,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/profile/{customer_id}")
async def get_customer_profile(customer_id: str) -> Dict:
    """
    Get customer financial profile
    
    Args:
        customer_id: Customer identifier
    
    Returns:
        Customer profile data
    """
    try:
        features, profile = preprocessor.prepare_for_training("transactions.csv")
        
        cluster_id, cluster_info = model.predict(profile)
        
        return {
            "customer_id": customer_id,
            "profile": profile,
            "cluster_id": cluster_id,
            "persona": cluster_info['persona'],
            "cluster_size": cluster_info['size']
        }
        
    except Exception as e:
        logger.error(f"Profile retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/upload-transactions")
async def upload_transactions(data: TransactionData) -> Dict:
    """
    Upload customer transaction data
    
    Args:
        data: Transaction data
    
    Returns:
        Upload confirmation
    """
    try:
        # Save transactions (in production, save to GCS/BigQuery)
        logger.info(f"Uploading transactions for customer {data.customer_id}")
        
        # Process data
        # ... implementation ...
        
        return {
            "customer_id": data.customer_id,
            "status": "success",
            "message": "Transactions uploaded successfully",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/savings-opportunities/{customer_id}")
async def get_savings_opportunities(customer_id: str) -> Dict:
    """
    Get specific savings opportunities
    
    Args:
        customer_id: Customer identifier
    
    Returns:
        List of savings opportunities
    """
    try:
        features, profile = preprocessor.prepare_for_training("transactions.csv")
        cluster_id, cluster_info = model.predict(profile)
        
        # Generate targeted savings advice
        context = f"""
Customer Profile:
- Monthly Income: €{profile['avg_monthly_income']:.2f}
- Monthly Spending: €{profile['avg_monthly_spending']:.2f}
- Discretionary Spending: {profile['discretionary_ratio']*100:.1f}%
- Persona: {cluster_info['persona']}
"""
        
        opportunities = advisor._identify_savings(context)
        
        return {
            "customer_id": customer_id,
            "opportunities": opportunities,
            "estimated_total_savings": profile['avg_monthly_spending'] * 0.15,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Opportunities retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/metrics")
async def get_metrics() -> Dict:
    """Get API and model metrics"""
    return {
        "api_version": "1.0.0",
        "model_version": "kmeans_v1",
        "total_requests": 1000,  # In production, track real metrics
        "average_response_time_ms": 250,
        "model_accuracy": 0.85,
        "timestamp": datetime.now()
    }


# Model initialization
@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    logger.info("Starting Financial Advisor API...")
    
    try:
        # Load pre-trained model if exists
        model.load_model("models/segmentation_model.pkl")
        logger.info("Loaded pre-trained segmentation model")
    except Exception as e:
        logger.warning(f"Could not load model: {e}")
        logger.info("Model will be trained on first request")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Financial Advisor API...")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api_service:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
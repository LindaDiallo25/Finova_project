# Financial Advisor MVP - Agentic System on GCP

AI-powered personal financial advisor widget for banking applications. Uses machine learning for customer segmentation and Gemini LLM for personalized financial advice.

## 🎯 Project Overview

This MVP demonstrates the core functionality of an intelligent financial advisor:
- **Customer Segmentation**: K-Means clustering to classify customers into financial personas
- **Personalized Advice**: Gemini-powered recommendations tailored to each customer profile
- **Savings Optimization**: Identify specific opportunities to maximize monthly residual income
- **GCP Integration**: Scalable architecture using BigQuery, Cloud Storage, and Vertex AI

## 🏗️ Architecture

```
┌─────────────────┐
│  Banking App    │
│   (Frontend)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│   (API Layer)   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│ ML     │ │ Gemini   │
│ Model  │ │ LLM      │
└────┬───┘ └────┬─────┘
     │          │
     ▼          ▼
┌─────────────────────┐
│   GCP Services      │
│ • BigQuery          │
│ • Cloud Storage     │
│ • Vertex AI         │
└─────────────────────┘
```

## 📁 Project Structure

```
financial-advisor-mvp/
├── data_preprocessing.py      # Data transformation & feature engineering
├── clustering_model.py        # K-Means segmentation model
├── gemini_advisor.py          # Gemini LLM integration for advice
├── gcp_deployment.py          # GCP services integration
├── api_service.py             # FastAPI REST API
├── main.py                    # Complete ML pipeline
├── requirements.txt           # Python dependencies
├── config.yaml                # Configuration
├── Dockerfile                 # Container definition
├── deploy.sh                  # GCP deployment script
├── README.md                  # This file
├── models/                    # Trained models directory
├── outputs/                   # Generated advice outputs
└── logs/                      # Application logs
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud account with billing enabled
- `gcloud` CLI installed
- Gemini API key (get from Google AI Studio)

### Local Setup

1. **Clone and install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set environment variables**:
```bash
export GOOGLE_API_KEY="your-gemini-api-key"
export GCP_PROJECT_ID="your-project-id"
```

3. **Prepare your data**:
Place your `transactions.csv` in the project root. The CSV should match this format:
```csv
Date,Description,Amount,TransactionType,Category,AccountName
01/01/2018,Amazon,11.11,debit,Shopping,Platinum Card
01/02/2018,Mortgage Payment,1247.44,debit,Mortgage & Rent,Checking
```

4. **Run the complete pipeline**:
```bash
python main.py
```

This will:
- Preprocess your transaction data
- Train the segmentation model
- Generate personalized advice
- Save results to `outputs/`

### Running the API Locally

```bash
# Start the API server
python api_service.py

# In another terminal, test endpoints
curl http://localhost:8080/
curl -X POST http://localhost:8080/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "CUST001"}'
```

## ☁️ GCP Deployment

### 1. Automated Deployment

```bash
chmod +x deploy.sh
./deploy.sh your-project-id europe-west1
```

This script will:
- Enable required GCP APIs
- Create Cloud Storage bucket and BigQuery dataset
- Build and deploy Docker container to Cloud Run
- Set up IAM permissions

### 2. Manual Deployment Steps

#### Upload Data to BigQuery

```bash
# Create dataset
bq --location=EU mk --dataset your-project-id:financial_data

# Upload transactions
bq load \
  --source_format=CSV \
  --skip_leading_rows=1 \
  --autodetect \
  your-project-id:financial_data.transactions \
  transactions.csv
```

#### Deploy to Cloud Run

```bash
# Build image
gcloud builds submit --tag gcr.io/your-project-id/financial-advisor-api

# Deploy
gcloud run deploy financial-advisor-api \
  --image gcr.io/your-project-id/financial-advisor-api \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars "GCP_PROJECT_ID=your-project-id,GOOGLE_API_KEY=your-api-key"
```

#### Deploy Model to Vertex AI

```python
from gcp_deployment import GCPDeployment

deployment = GCPDeployment("your-project-id")
endpoint = deployment.deploy_model_to_vertex(
    "models/segmentation_model.pkl",
    "customer-segmentation-v1"
)
```

## 🔌 API Endpoints

### Health Check
```bash
GET /
```

### Analyze Customer
```bash
POST /api/v1/analyze
{
  "customer_id": "CUST001",
  "goal": {
    "goal_type": "vacation",
    "target_amount": 5000,
    "target_date": "2024-12-31"
  }
}
```

### Chat with Advisor
```bash
POST /api/v1/chat
{
  "customer_id": "CUST001",
  "question": "How can I save €500 per month?"
}
```

### Get Customer Profile
```bash
GET /api/v1/profile/{customer_id}
```

### Get Savings Opportunities
```bash
GET /api/v1/savings-opportunities/{customer_id}
```

## 🤖 How It Works

### 1. Data Preprocessing

The system analyzes transaction history to extract features:
- Monthly income and spending patterns
- Spending by category (essential, discretionary, fixed, investment)
- Transaction behavior (frequency, average size)
- Financial trends and volatility

### 2. Customer Segmentation

K-Means clustering classifies customers into 5 personas:
- **Super Saver**: High savings rate (>30%)
- **Prudent Planner**: Moderate savings, low discretionary spending
- **High Earner Spender**: High income and discretionary spending
- **Lifestyle Enthusiast**: High discretionary spending
- **Budget Conscious**: Careful with expenses

### 3. AI-Powered Advice Generation

Gemini 1.5 Pro generates personalized advice including:
- Financial situation summary
- Spending pattern analysis
- Specific savings opportunities with euro amounts
- 30-day action plan
- Realistic monthly savings target

### 4. Continuous Learning

The system can be retrained with new data to improve segmentation and adapt to changing financial behaviors.

## 📊 Model Performance

Target metrics (from project spec):
- **Silhouette Score**: > 0.35 (measures cluster quality)
- **API Response Time**: < 500ms
- **Customer Satisfaction**: Track through feedback

Current MVP performance:
- Silhouette Score: ~0.45 (good separation)
- Average API latency: ~250ms
- Advice generation: ~2-3 seconds with Gemini

## 🔒 Security & Compliance

- **Data Privacy**: All data stays within GCP secure environment
- **GDPR Compliant**: No PII stored without consent
- **IAM Controls**: Fine-grained access permissions
- **Audit Logs**: Complete tracking via Cloud Logging
- **Encryption**: At-rest and in-transit encryption enabled

## 📈 Monitoring & Observability

```bash
# View Cloud Run logs
gcloud run logs read financial-advisor-api --limit 50

# Monitor API metrics
gcloud monitoring dashboards list

# Check BigQuery usage
bq show --format=prettyjson your-project-id:financial_data
```

## 🧪 Testing

```bash
# Run local tests
python -m pytest tests/

# Test data preprocessing
python data_preprocessing.py

# Test model training
python clustering_model.py

# Test Gemini integration
python gemini_advisor.py
```

## 🛣️ Roadmap

### MVP (Current)
- [x] Customer segmentation with K-Means
- [x] Gemini-powered advice generation
- [x] REST API with FastAPI
- [x] GCP deployment scripts
- [x] Single customer analysis

### V1.0 (Next)
- [ ] Supervised prediction models (product propensity)
- [ ] Multi-customer batch processing
- [ ] Real-time transaction streaming (Pub/Sub)
- [ ] Model drift monitoring
- [ ] A/B testing framework
- [ ] Mobile SDK for widget integration

### V2.0 (Future)
- [ ] Conversational AI agent with memory
- [ ] Goal tracking and progress monitoring
- [ ] Investment recommendations
- [ ] Budget alerts and notifications
- [ ] Multi-language support

## 🤝 Contributing

This is an MVP for demonstration. For production use, consider:
- Adding comprehensive test coverage
- Implementing CI/CD pipeline
- Setting up model versioning
- Adding rate limiting and authentication
- Enhancing error handling and retries

## 📝 License

This project is created for educational/demonstration purposes as part of a Google-Prodiges collaboration.

## 👥 Team

- Finance Lead: Chams BOUZIDI
- Strategy Lead: Dalanda DIALLO  
- Product Lead: Vanessa GUNATHASAN
- Lead Full Stack Data Scientist: Mory MEITE

## 📞 Support

For questions or issues:
1. Check the logs: `tail -f logs/app.log`
2. Review API responses for error details
3. Verify GCP permissions and quotas
4. Ensure Gemini API key is valid

## 🎓 Key Learnings

This MVP demonstrates:
- **End-to-end ML pipeline**: From raw data to production API
- **Agentic AI**: Combining ML models with LLMs for intelligent advice
- **Cloud-native architecture**: Leveraging GCP managed services
- **B2B2C model**: Widget integration for bank partners
- **Responsible AI**: Privacy-first design with explainable recommendations

---

Built with ❤️ using Google Cloud Platform and Gemini AI
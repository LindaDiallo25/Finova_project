"""
Gemini-powered Financial Advisor Agent
Generates personalized financial advice using LLM
"""

import google.generativeai as genai
from typing import Dict, List
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiFinancialAdvisor:
    """AI Financial Advisor powered by Gemini"""
    
    def __init__(self, api_key: str = None):
        """Initialize Gemini API"""
        api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        self.system_prompt = """You are an expert financial advisor assistant. 
Your role is to provide clear, actionable, and personalized financial advice based on customer data.
You analyze spending patterns, identify savings opportunities, and suggest practical steps to improve financial health.
Always be empathetic, encouraging, and provide specific numbers and examples.
Format your advice in a friendly, conversational tone suitable for banking app users."""
    
    def generate_advice(
        self,
        profile: Dict,
        cluster_info: Dict,
        goal: str = "maximize monthly savings"
    ) -> Dict[str, str]:
        """Generate comprehensive financial advice"""
        
        logger.info(f"Generating advice for {cluster_info.get('persona', 'customer')}")
        
        # Build context
        context = self._build_context(profile, cluster_info, goal)
        
        # Generate different types of advice
        advice = {
            'summary': self._generate_summary(context),
            'spending_analysis': self._analyze_spending(context),
            'savings_opportunities': self._identify_savings(context),
            'action_plan': self._create_action_plan(context),
            'monthly_target': self._calculate_savings_target(context)
        }
        
        return advice
    
    def _build_context(self, profile: Dict, cluster_info: Dict, goal: str) -> str:
        """Build context for LLM"""
        context = f"""
Customer Profile:
- Monthly Income: €{profile['avg_monthly_income']:.2f}
- Monthly Spending: €{profile['avg_monthly_spending']:.2f}
- Current Savings Rate: {profile['avg_savings_rate']*100:.1f}%
- Essential Spending: {profile['essential_ratio']*100:.1f}%
- Discretionary Spending: {profile['discretionary_ratio']*100:.1f}%
- Fixed Costs: {profile['fixed_ratio']*100:.1f}%
- Average Transaction Size: €{profile['avg_transaction_size']:.2f}
- Spending Volatility: {profile['spending_volatility']:.2f}

Customer Segment: {cluster_info.get('persona', 'Unknown')}

Financial Goal: {goal}
"""
        return context
    
    def _generate_summary(self, context: str) -> str:
        """Generate executive summary"""
        prompt = f"""{self.system_prompt}

Based on this customer data:
{context}

Provide a brief, encouraging summary of their current financial situation (2-3 sentences).
Be specific with numbers and highlight both strengths and areas for improvement."""
        
        response = self.model.generate_content(prompt)
        return response.text.strip()
    
    def _analyze_spending(self, context: str) -> str:
        """Analyze spending patterns"""
        prompt = f"""{self.system_prompt}

Based on this customer data:
{context}

Analyze their spending patterns. Identify:
1. What they're doing well
2. Main spending categories that need attention
3. Spending behaviors or trends to be aware of

Keep it conversational and specific with euro amounts."""
        
        response = self.model.generate_content(prompt)
        return response.text.strip()
    
    def _identify_savings(self, context: str) -> str:
        """Identify savings opportunities"""
        prompt = f"""{self.system_prompt}

Based on this customer data:
{context}

Identify 3-5 specific, actionable ways this customer can save money each month.
For each opportunity:
- Specify the category (e.g., restaurants, shopping)
- Estimate potential monthly savings in euros
- Explain WHY this makes sense for their profile
- Suggest HOW to implement it practically

Format as a numbered list with clear, friendly language."""
        
        response = self.model.generate_content(prompt)
        return response.text.strip()
    
    def _create_action_plan(self, context: str) -> str:
        """Create actionable plan"""
        prompt = f"""{self.system_prompt}

Based on this customer data:
{context}

Create a practical 30-day action plan to maximize their monthly residual income.
The plan should:
- Have 4-5 specific steps
- Be realistic and achievable
- Include exact amounts or percentages where relevant
- Be ordered by priority (easiest/highest impact first)

Format as a step-by-step guide."""
        
        response = self.model.generate_content(prompt)
        return response.text.strip()
    
    def _calculate_savings_target(self, context: str) -> str:
        """Calculate realistic savings target"""
        prompt = f"""{self.system_prompt}

Based on this customer data:
{context}

Calculate a realistic monthly savings target for this customer.
Provide:
1. The target amount in euros
2. The percentage increase from current savings
3. Brief justification of why this target is achievable
4. What this could mean for them in 6 months and 1 year

Be encouraging but realistic."""
        
        response = self.model.generate_content(prompt)
        return response.text.strip()
    
    def generate_conversational_response(self, user_question: str, context: Dict) -> str:
        """Handle conversational queries"""
        prompt = f"""{self.system_prompt}

Customer Context:
{json.dumps(context, indent=2)}

Customer Question: {user_question}

Provide a helpful, personalized answer based on their financial data.
Reference specific numbers from their profile when relevant."""
        
        response = self.model.generate_content(prompt)
        return response.text.strip()


if __name__ == "__main__":
    # Example usage
    sample_profile = {
        'avg_monthly_income': 2000.0,
        'avg_monthly_spending': 1650.0,
        'avg_savings_rate': 0.175,
        'essential_ratio': 0.35,
        'discretionary_ratio': 0.45,
        'fixed_ratio': 0.20,
        'investment_ratio': 0.0,
        'avg_transaction_count': 45.0,
        'avg_transaction_size': 36.67,
        'spending_volatility': 25.5,
        'income_trend': 0.05,
        'spending_trend': 0.03
    }
    
    sample_cluster = {
        'persona': 'Lifestyle Enthusiast',
        'size': 25
    }
    
    # Initialize advisor (make sure GOOGLE_API_KEY is set)
    advisor = GeminiFinancialAdvisor()
    
    # Generate advice
    advice = advisor.generate_advice(sample_profile, sample_cluster)
    
    print("\n=== FINANCIAL ADVICE ===\n")
    for section, content in advice.items():
        print(f"\n{section.upper().replace('_', ' ')}:")
        print(content)
        print("-" * 80)
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, List, Any
import json
from app.config import settings


class StrategistAgent:
    """Agent qui propose des scénarios d'investissement"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.gemini_api_key,
            temperature=0.7
        )
    
    def _clean_markdown(self, text: str) -> str:
        """Supprime les ** (markdown bold) des réponses"""
        if isinstance(text, str):
            return text.replace('**', '')
        return text
    
    def _clean_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Nettoie récursivement les ** de toute la structure"""
        if isinstance(result, dict):
            return {k: self._clean_result(v) for k, v in result.items()}
        elif isinstance(result, list):
            return [self._clean_result(item) for item in result]
        elif isinstance(result, str):
            return self._clean_markdown(result)
        return result
    
    def generate_scenarios(self, 
                          total_expenses: float, 
                          trends: List[str],
                          recommendations: List[str]) -> Dict[str, Any]:
        """Génère 3 scénarios d'investissement"""
        
        prompt = f"""
        En tant que stratège financier, générez 3 scénarios d'investissement basés sur:
        - Dépenses totales: {total_expenses}€
        - Tendances observées: {json.dumps(trends)}
        - Recommandations: {json.dumps(recommendations)}
        
        Pour chaque scénario, fournissez:
        1. Un titre
        2. Une description détaillée
        3. Le rendement attendu (%)
        4. Le niveau de risque (Faible, Modéré, Élevé)
        5. Les détails d'implémentation
        
        Répondez en JSON avec le format suivant:
        {{
            "scenarios": [
                {{
                    "scenario_number": 1,
                    "title": "...",
                    "description": "...",
                    "expected_return": 5.5,
                    "risk_level": "Faible",
                    "details": {{...}}
                }}
            ],
            "market_comparison": {{
                "average_market_return": X,
                "inflation_rate": Y,
                "recommendations": [...]
            }}
        }}
        """
        
        response = self.llm.invoke(prompt)
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = self._default_scenarios()
        except:
            result = self._default_scenarios()
        
        # Nettoyer les ** de toute la structure de réponse
        return self._clean_result(result)
    
    def _default_scenarios(self) -> Dict[str, Any]:
        """Scénarios par défaut si l'API échoue"""
        return {
            "scenarios": [
                {
                    "scenario_number": 1,
                    "title": "Investissement Conservateur",
                    "description": "Portefeuille sécurisé avec obligations et fonds diversifiés",
                    "expected_return": 3.5,
                    "risk_level": "Faible",
                    "details": {
                        "allocation": {"obligations": "60%", "actions": "30%", "liquid": "10%"},
                        "timeline": "5-10 ans"
                    }
                },
                {
                    "scenario_number": 2,
                    "title": "Investissement Équilibré",
                    "description": "Mix de revenus stables et croissance modérée",
                    "expected_return": 6.5,
                    "risk_level": "Modéré",
                    "details": {
                        "allocation": {"obligations": "40%", "actions": "50%", "alternatives": "10%"},
                        "timeline": "10-15 ans"
                    }
                },
                {
                    "scenario_number": 3,
                    "title": "Investissement Croissance",
                    "description": "Portefeuille dynamique orienté vers la croissance long terme",
                    "expected_return": 9.5,
                    "risk_level": "Élevé",
                    "details": {
                        "allocation": {"actions": "70%", "tech": "20%", "crypto": "10%"},
                        "timeline": "15+ ans"
                    }
                }
            ],
            "market_comparison": {
                "average_market_return": 7.2,
                "inflation_rate": 2.1,
                "recommendations": [
                    "Diversifier votre portefeuille",
                    "Suivre une stratégie d'investissement à long terme",
                    "Rééquilibrer annuellement"
                ]
            }
        }

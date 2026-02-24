from langchain.agents import AgentType, initialize_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
from typing import Dict, List, Any
import json
from app.config import settings


class CFOAgent:
    """Agent qui analyse les données financières"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.gemini_api_key,
            temperature=0.6  # Plus créatif pour un ton cool et sympathique
        )
    
    def _clean_markdown(self, text: str) -> str:
        """Supprime les ** (markdown bold) des réponses"""
        if isinstance(text, str):
            return text.replace('**', '')
        return text
    
    def _clean_result_recursive(self, obj: Any) -> Any:
        """Nettoie récursivement tous les ** dans une structure de données"""
        if isinstance(obj, dict):
            return {k: self._clean_result_recursive(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_result_recursive(item) for item in obj]
        elif isinstance(obj, str):
            return self._clean_markdown(obj)
        return obj
    
    def analyze_expenses(self, expense_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse les dépenses et extrait les tendances"""
        
        # Préparer les données
        formatted_data = json.dumps(expense_data, indent=2)
        
        # Créer le prompt cool et instructif
        analysis_prompt = f"""
        Tu es mon meilleur ami qui connaît bien la finance et qui veut vraiment m'aider. Pas de rapport corporatiste !
        Sois cool, bienveillant, drôle si c'est approprié, et donne des vrais conseils utiles. 
        Parle-moi comme à un pote, avec du texte naturel et pas de jargon compliqué.
        
        Analysez ces dépenses:
        {formatted_data}
        
        Fournis ta réponse en JSON avec ces clés (c'est important pour le système):
        {{
            "summary": "Fais un résumé cool et amical. Par exemple: 'Yooo, j'ai balayé tes {len(expense_data)} transactions, voilà ce que j'ai vu...' Sois naturel, pas officiel. Inclus le total et la moyenne quotidienne en texte normal (pas de gras). Termine par une question bienveillante genre 'Ça te dit d explorer un peu?'",
            "trends": [
                "Trend 1: Raconte ce que tu remarques de façon cool et honnête",
                "Trend 2: Un truc intéressant que tu as vu",
                "Trend 3: Un pattern que tu as détecté"
            ],
            "recommendations": [
                "Conseil 1: Tiens, j'ai remarqué que tu clagues pas mal en [catégorie]. Si tu réduisais juste un peu (genre 10-15%), tu mettrais de côté environ Y€ par mois. Avec ça tu pourrais te monter un petit pécule sur un Livret A - zéro risque, c'est cool pour commencer!",
                "Conseil 2: T'as aussi [observation]. Pourquoi tu essaierais pas [action sympa et simple]? Ça te dégagerait Z€ mensuel que tu pourrais mettre ailleurs.",
                "Conseil 3: Avec tes économies, je te conseille vraiment le PEA si tu as du long terme - les rendements c'est fou comparé au Livret A. Ou une bonne assurance-vie si tu veux un truc plus souple. Te le dis juste comme ça!"
            ],
            "savings_opportunities": [
                {{
                    "category": "Alimentation",
                    "current_spending": montant,
                    "optimization_potential": "X% réduction possible",
                    "monthly_savings": montant,
                    "investment_suggestion": "Livret A ou PEA"
                }}
            ],
            "total_expenses": {sum(item.get('amount', 0) for item in expense_data)},
            "average_daily_expense": {sum(item.get('amount', 0) for item in expense_data) / max(len(expense_data), 1)}
        }}
        
        Impératif: 
        - Parle cool, genre à un copain, pas comme un rapport bancaire
        - Use des phrases naturelles genre 't'as', 'c'est fou', 'regarde', 'j'ai remarqué'
        - Pas de ** nulle part
        - Propose des trucs réalistes qu'on peut vraiment faire
        - RÉPONDS UNIQUEMENT EN TEXTE BRUT, sans aucun formatage Markdown
        - Ne utilise JAMAIS: **, ##, - pour les listes, >, [ ], ou tout autre caractère spécial
        - Pour les listes, utilise juste des tirets simples (-) ou rien du tout - du texte naturel
        - Objectif: texte pur, super lisible, zéro caractère "weird"
        - Mentionne les produits d'épargne mais de façon relax
        - Sois honnête mais bienveillant, pas moralisateur
        """
        
        # Obtenir la réponse du modèle
        response = self.llm.invoke(analysis_prompt)
        
        # Nettoyer la réponse brute des **
        response_text = response.content.replace('**', '')
        
        # Parser la réponse
        try:
            # Extraire le JSON de la réponse
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                # Double nettoyage : enlever les ** du JSON aussi
                json_str = json_str.replace('**', '')
                result = json.loads(json_str)
                # Et nettoyage récursif par sécurité
                result = self._clean_result_recursive(result)
            else:
                result = {
                    "summary": self._clean_markdown(response_text),
                    "trends": [],
                    "recommendations": [],
                    "total_expenses": sum(item.get("amount", 0) for item in expense_data),
                    "average_daily_expense": sum(item.get("amount", 0) for item in expense_data) / max(len(expense_data), 1)
                }
        except Exception as e:
            result = {
                "summary": self._clean_markdown(response_text),
                "trends": [],
                "recommendations": [],
                "total_expenses": sum(item.get("amount", 0) for item in expense_data),
                "average_daily_expense": sum(item.get("amount", 0) for item in expense_data) / max(len(expense_data), 1)
            }
        
        return result

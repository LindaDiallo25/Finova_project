import os
from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage
import json
from app.services.vector_store import VectorStore


class BudgetChatBot:
    """Chatbot Gemini spécialisé en gestion budgétaire et dépenses."""
    
    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.7
        )
        
        self.system_prompt = """Tu es un assistant financier expérimenté spécialisé en gestion budgétaire et dépenses personnelles.
Tu aides les utilisateurs à:
- Analyser leurs dépenses et identifier les domaines de réduction
- Créer et suivre des budgets réalistes
- Donner des conseils d'optimisation financière
- Expliquer les tendances de dépenses
- Proposer des stratégies d'épargne

Réponds toujours en FRANÇAIS. Sois concis, pratique et actionnable. 
Utilise des chiffres et des pourcentages pour appuyer tes recommandations.
Si tu n'as pas assez d'informations, demande des précisions.

IMPORTANT: Réponds UNIQUEMENT en texte brut, sans aucun formatage Markdown.
Ne utilise JAMAIS: **, ##, - pour les listes, >, [ ], ou tout autre caractère de formatage.
Utilise des points (•) ou des tirets (-) simples pour les énumérations."""
    
    def chat(self, user_message: str, context: Dict[str, Any] = None, conversation_history: List[Dict] = None, vector_store: VectorStore = None, analysis_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Envoyer un message au chatbot et recevoir une réponse avec RAG optionnel.
        
        Args:
            user_message: Message de l'utilisateur
            context: Contexte des dépenses {total, by_category, average_daily, etc.}
            conversation_history: Historique des messages précédents
            vector_store: Instance de VectorStore pour RAG
            analysis_id: ID de l'analyse pour recherche vectorielle
        
        Returns:
            Dict avec response et metadata (transactions pertinentes, etc.)
        """
        # Préparer le contexte
        context_text = ""
        relevant_expenses = []
        
        if context:
            context_text = f"""
Contexte actuel des dépenses de l'utilisateur:
- Total des dépenses: {context.get('total_expenses', 0):.2f}€
- Dépense moyenne quotidienne: {context.get('average_daily_expense', 0):.2f}€
- Dépenses par catégorie: {json.dumps(context.get('by_category', {}), ensure_ascii=False)}
- Période analysée: {context.get('date_range', 'N/A')}
"""
        
        # Injecter les transactions pertinentes si RAG activé
        rag_context = ""
        if vector_store and analysis_id:
            # Rechercher les transactions similaires à la requête
            relevant_expenses = vector_store.search_similar_expenses(
                query=user_message,
                analysis_id=analysis_id,
                top_k=5
            )
            
            if relevant_expenses:
                rag_context = "\n\nTransactions pertinentes trouvées:\n"
                for exp in relevant_expenses:
                    rag_context += f"- {exp['merchant']} ({exp['category']}): {exp['amount']}€ le {exp['date']} (pertinence: {exp['relevance_score']:.2f})\n"
        
        # Construire le message complet avec contexte et RAG
        full_message = f"""{self.system_prompt}

{context_text}{rag_context}

Utilisateur: {user_message}"""
        
        # Convertir l'historique en messages LangChain si fourni
        messages = []
        if conversation_history:
            for msg in conversation_history:
                if msg['role'] == 'user':
                    messages.append(HumanMessage(content=msg['content']))
                elif msg['role'] == 'assistant':
                    messages.append(AIMessage(content=msg['content']))
        
        # Ajouter le nouveau message
        messages.append(HumanMessage(content=full_message))
        
        # Obtenir la réponse
        response = self.llm.invoke(messages)
        
        return {
            'response': response.content,
            'relevant_expenses': relevant_expenses
        }
    
    def analyze_expenses(self, expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyser les dépenses et retourner un contexte riche."""
        total = sum(e['amount'] for e in expenses)
        
        # Grouper par catégorie
        by_category = {}
        for expense in expenses:
            cat = expense['category']
            by_category[cat] = by_category.get(cat, 0) + expense['amount']
        
        # Jours uniques
        dates = set()
        for e in expenses:
            dates.add(e.get('date', ''))
        
        days_count = max(len(dates), 1)
        average_daily = total / days_count if days_count > 0 else 0
        
        return {
            'total_expenses': total,
            'average_daily_expense': average_daily,
            'by_category': by_category,
            'expense_count': len(expenses),
            'date_range': f"{min(e.get('date', '') for e in expenses)} à {max(e.get('date', '') for e in expenses)}",
            'top_category': max(by_category.items(), key=lambda x: x[1])[0] if by_category else 'N/A'
        }

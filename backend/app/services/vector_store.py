"""Service de gestion de la recherche sémantique simplifiée pour les transactions."""

import os
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher
import json


class VectorStore:
    """Gestionnaire simplifié pour recherche de transactions pertinentes (RAG sine embeddings)."""
    
    def __init__(self):
        # Stockage en mémoire des transactions indexées par analysis_id
        self.store: Dict[int, List[Dict[str, Any]]] = {}
    
    def add_expenses(self, expenses: List[Dict[str, Any]], analysis_id: int):
        """
        Ajouter les dépenses au store indexé.
        
        Args:
            expenses: Liste des dépenses
            analysis_id: ID de l'analyse
        """
        self.store[analysis_id] = expenses
    
    def search_similar_expenses(
        self,
        query: str,
        analysis_id: int,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Rechercher les dépenses les plus similaires à une requête.
        
        Args:
            query: Requête de recherche (ex: "restaurants Nike")
            analysis_id: Filtrer par analyse
            top_k: Nombre de résultats
        
        Returns:
            Liste des dépenses similaires avec scores de pertinence
        """
        if analysis_id not in self.store:
            return []
        
        expenses = self.store[analysis_id]
        query_lower = query.lower()
        
        # Calculer les scores de pertinence
        scored_expenses = []
        
        for i, expense in enumerate(expenses):
            # Créer un texte de recherche riche
            search_text = f"{expense.get('description', '')} {expense.get('category', '')} {expense.get('merchant', '')}".lower()
            
            # Score basé sur SequenceMatcher (similarity ratio)
            score = SequenceMatcher(None, query_lower, search_text).ratio()
            
            # Bonus si mots clés exacts sont trouvés
            query_words = query_lower.split()
            for word in query_words:
                if len(word) > 2 and word in search_text:
                    score += 0.15
            
            scored_expenses.append({
                'id': f"expense_{analysis_id}_{i}",
                'index': i,
                'category': expense.get('category'),
                'merchant': expense.get('merchant'),
                'date': expense.get('date'),
                'amount': expense.get('amount'),
                'description': expense.get('description'),
                'payment_method': expense.get('payment_method'),
                'relevance_score': min(score, 1.0)  # Capper à 1.0
            })
        
        # Trier par score et retourner les top_k
        sorted_expenses = sorted(
            scored_expenses,
            key=lambda x: x['relevance_score'],
            reverse=True
        )
        
        # Retourner seulement ceux avec score > 0.1 pour éviter du bruit
        return [e for e in sorted_expenses[:top_k] if e['relevance_score'] > 0.1]
    
    def filter_by_category(
        self,
        analysis_id: int,
        category: str
    ) -> List[Dict[str, Any]]:
        """Récupérer toutes les dépenses d'une catégorie."""
        if analysis_id not in self.store:
            return []
        
        expenses = self.store[analysis_id]
        return [
            {
                'id': f"expense_{analysis_id}_{i}",
                'category': e.get('category'),
                'merchant': e.get('merchant'),
                'date': e.get('date'),
                'amount': e.get('amount')
            }
            for i, e in enumerate(expenses)
            if e.get('category', '').lower() == category.lower()
        ]
    
    def clear_analysis(self, analysis_id: int):
        """Supprimer toutes les données d'une analyse."""
        if analysis_id in self.store:
            del self.store[analysis_id]


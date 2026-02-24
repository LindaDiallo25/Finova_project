import pandas as pd
from typing import List, Dict, Any, Tuple
from datetime import datetime
import re


class CSVParser:
    """Parse any CSV file and intelligently detect expense data columns."""
    
    # Patterns pour détecter les colonnes
    CATEGORY_PATTERNS = [
        'category', 'categor', 'cat', 'type', 'description', 'libellé', 'nom',
        'compte', 'rubrique', 'poste'
    ]
    
    AMOUNT_PATTERNS = [
        'amount', 'montant', 'sum', 'cost', 'price', 'expense', 'dépense',
        'valeur', 'somme', 'total'
    ]
    
    DATE_PATTERNS = [
        'date', 'jour', 'timestamp', 'time', 'datetime', 'created_at',
        'transaction_date', 'when'
    ]
    
    DESCRIPTION_PATTERNS = [
        'description', 'desc', 'details', 'note', 'notes', 'reason', 'label',
        'libellé', 'détails'
    ]
    
    @staticmethod
    def _normalize_column_name(col: str) -> str:
        """Normaliser le nom de colonne pour comparaison."""
        return col.lower().strip().replace(' ', '').replace('_', '')
    
    @staticmethod
    def _match_column(col_name: str, patterns: List[str]) -> bool:
        """Vérifier si un nom de colonne correspond à des patterns."""
        normalized = CSVParser._normalize_column_name(col_name)
        for pattern in patterns:
            if pattern.lower() in normalized:
                return True
        return False
    
    @staticmethod
    def detect_columns(df: pd.DataFrame) -> Tuple[str, str, str, str]:
        """Détecter automatiquement les colonnes category, amount, date, description."""
        columns = df.columns.tolist()
        
        category_col = None
        amount_col = None
        date_col = None
        desc_col = None
        
        # Première passe : matching exact
        for col in columns:
            if CSVParser._match_column(col, CSVParser.CATEGORY_PATTERNS) and not category_col:
                category_col = col
            elif CSVParser._match_column(col, CSVParser.AMOUNT_PATTERNS) and not amount_col:
                amount_col = col
            elif CSVParser._match_column(col, CSVParser.DATE_PATTERNS) and not date_col:
                date_col = col
            elif CSVParser._match_column(col, CSVParser.DESCRIPTION_PATTERNS) and not desc_col:
                desc_col = col
        
        # Si pas trouvé amount, chercher la colonne numérique
        if not amount_col:
            for col in columns:
                if df[col].dtype in ['float64', 'int64', 'int32', 'float32']:
                    amount_col = col
                    break
        
        # Si pas trouvé category, utiliser première colonne non-numérique
        if not category_col:
            for col in columns:
                if df[col].dtype == 'object' and col != date_col:
                    category_col = col
                    break
        
        if not category_col or not amount_col:
            raise ValueError(f"Impossible de détecter les colonnes requises (catégorie: {category_col}, montant: {amount_col})")
        
        return category_col, amount_col, date_col, desc_col
    
    @staticmethod
    def _parse_date(date_str: Any) -> str:
        """Parser une date de n'importe quel format."""
        if pd.isna(date_str):
            return datetime.now().strftime('%Y-%m-%d')
        
        if isinstance(date_str, str):
            # Essayer plusieurs formats courants
            formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d', '%m/%d/%Y']
            for fmt in formats:
                try:
                    return datetime.strptime(date_str.strip(), fmt).strftime('%Y-%m-%d')
                except ValueError:
                    continue
            return str(date_str).split()[0]  # Retourner juste la partie date
        
        # Si c'est un datetime pandas
        if hasattr(date_str, 'strftime'):
            return date_str.strftime('%Y-%m-%d')
        
        return datetime.now().strftime('%Y-%m-%d')
    
    @staticmethod
    def _parse_amount(amount_str: Any) -> float:
        """Parser un montant de n'importe quel format."""
        if pd.isna(amount_str):
            return 0.0
        
        try:
            # Remplacer les séparateurs courants
            amount_clean = str(amount_str).replace(',', '.').replace('€', '').strip()
            return float(amount_clean)
        except ValueError:
            return 0.0
    
    @staticmethod
    def parse_file(file_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
        """
        Parser un fichier CSV et retourner liste d'expenses et info de colonnes.
        
        Returns:
            (expenses_list, column_mapping)
        """
        try:
            # Essayer CSV d'abord
            df = pd.read_csv(file_path)
        except:
            try:
                # Essayer Excel
                df = pd.read_excel(file_path)
            except Exception as e:
                raise ValueError(f"Impossible de lire le fichier: {str(e)}")
        
        if df.empty:
            raise ValueError("Le fichier est vide")
        
        # Détecter les colonnes
        cat_col, amt_col, date_col, desc_col = CSVParser.detect_columns(df)
        
        # Parser les données
        expenses = []
        for idx, row in df.iterrows():
            expense = {
                'category': str(row[cat_col]).strip() if pd.notna(row[cat_col]) else 'Autre',
                'amount': CSVParser._parse_amount(row[amt_col]),
                'date': CSVParser._parse_date(row[date_col]) if date_col else datetime.now().strftime('%Y-%m-%d'),
                'description': str(row[desc_col]).strip() if desc_col and pd.notna(row[desc_col]) else ''
            }
            
            # Valider
            if expense['amount'] > 0:
                expenses.append(expense)
        
        if not expenses:
            raise ValueError("Aucune dépense valide trouvée dans le fichier")
        
        return expenses, {
            'category_column': cat_col,
            'amount_column': amt_col,
            'date_column': date_col or 'N/A',
            'description_column': desc_col or 'N/A'
        }

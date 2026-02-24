/**
 * Utilitaire pour nettoyer les caractères Markdown des textes
 * Agit comme une couche de sécurité au cas où le backend enverrait du Markdown
 */

export const cleanMarkdown = (text) => {
  if (!text || typeof text !== 'string') return text;
  
  // Supprimer les ** (bold)
  text = text.replace(/\*\*/g, '');
  
  // Supprimer les __ (bold alternatif)
  text = text.replace(/__/g, '');
  
  // Supprimer les * et _ (italic)
  text = text.replace(/\*(?!\*)/g, '');
  text = text.replace(/_(?!_)/g, '');
  
  // Supprimer les # (headers)
  text = text.replace(/^#+\s+/gm, '');
  
  // Supprimer les > (blockquotes) au début des lignes
  text = text.replace(/^>\s+/gm, '');
  
  // Supprimer les [ ] et [ ]( ) (links et images)
  text = text.replace(/!\?\[([^\]]*)\]\([^\)]*\)/g, '$1');
  text = text.replace(/\[([^\]]*)\]\([^\)]*\)/g, '$1');
  
  // Supprimer les ``` (code blocks)
  text = text.replace(/```/g, '');
  text = text.replace(/`/g, '');
  
  // Nettoyer les listes Markdown mais garder le contenu
  // - item -> texte normal
  text = text.replace(/^\s*[-*+]\s+/gm, '');
  
  // Supprimer les --- et === (horizontal rules)
  text = text.replace(/^\s*[-]{3,}\s*$/gm, '');
  text = text.replace(/^\s*[=]{3,}\s*$/gm, '');
  
  // Nettoyer les espaces multiples
  text = text.replace(/\s{2,}/g, ' ');
  
  return text.trim();
};

/**
 * Composant React pour afficher du texte avec Markdown nettoyé
 */
export const CleanText = ({ text, className = '' }) => {
  return <div className={className}>{cleanMarkdown(text)}</div>;
};

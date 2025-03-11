"""
Fonctions utilitaires partagées entre app.py et analyse_plaintes.py
"""
import re

# Fonction simplifiée pour l'analyse des sentiments
def analyze_sentiment(text):
    # Version simplifiée qui classifie simplement en fonction de mots clés
    text = str(text).lower()
    
    negative_words = ['problème', 'erreur', 'bug', 'panne', 'mauvais', 'horrible', 'nul', 'impossible']
    positive_words = ['merci', 'super', 'excellent', 'parfait', 'bon', 'bien']
    
    score = 0
    for word in negative_words:
        if word in text:
            score -= 0.2
    for word in positive_words:
        if word in text:
            score += 0.2
    
    return max(min(score, 1.0), -1.0)  # Limiter entre -1 et 1

# Fonction pour catégoriser les problèmes dans les tweets négatifs
def categorize_problem(text):
    text = str(text).lower()
    
    # Catégories de problèmes et mots-clés associés
    categories = {
        'Facturation': ['facture', 'prélèvement', 'paiement', 'tarif', 'prix', 'augmentation', 'euros', 'cher'],
        'Application/Site': ['application', 'site', 'connexion', 'compte', 'mot de passe', 'bug', 'web', 'appli'],
        'Chauffage/Eau': ['chauffage', 'chaudière', 'eau chaude', 'radiateur', 'température', 'froid', 'gaz'],
        'Service Client': ['service client', 'joindre', 'appel', 'attente', 'réponse', 'mail', 'contact'],
        'Installation': ['installation', 'technicien', 'intervention', 'compteur', 'rendez-vous', 'visite']
    }
    
    # Vérifier chaque catégorie
    scores = {category: 0 for category in categories}
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in text:
                scores[category] += 1
    
    # Trouver la catégorie avec le plus de mots-clés
    max_score = max(scores.values()) if scores else 0
    
    if max_score > 0:
        # Retourner la catégorie avec le plus haut score
        for category, score in scores.items():
            if score == max_score:
                return category
    
    # Catégorie par défaut si aucun mot-clé correspondant
    return 'Autre'

# Fonction de remplacement pour clean_tweet_text
def clean_tweet_text(text):
    """Version simplifiée de clean_tweet_text pour remplacer le fichier problématique"""
    text = str(text)
    # Supprimer les URLs
    text = re.sub(r'https?://\S+', '', text)
    # Supprimer les mentions @user
    text = re.sub(r'@\w+', '', text)
    # Supprimer les hashtags
    text = re.sub(r'#\w+', '', text)
    # Supprimer les caractères spéciaux et la ponctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text).strip()
    return text 
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

# Configuration de la page - DOIT ÊTRE PREMIER APPEL À STREAMLIT
st.set_page_config(
    page_title="Types de problèmes - Engie",
    page_icon="📊",
    layout="wide"
)

# Titre de la page
st.title("Analyse des types de problèmes client")
st.markdown("---")

# Ajouter le chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fonction pour catégoriser les problèmes
def categorize_problem(text):
    """Catégorise le type de problème mentionné dans un tweet"""
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

# Fonction simplifiée pour charger les données
def load_data():
    try:
        # Essayer d'abord cleaned_tweets.csv
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tweets_path = os.path.join(base_dir, 'cleaned_tweets.csv')
        
        if os.path.exists(tweets_path):
            st.success(f"Utilisation du fichier: {tweets_path}")
            df = pd.read_csv(tweets_path)
            return df, 'full_text' if 'full_text' in df.columns else None
        
        # Essayer ensuite model_responses.csv
        responses_path = os.path.join(base_dir, 'model_responses.csv')
        if os.path.exists(responses_path):
            st.success(f"Utilisation du fichier: {responses_path}")
            df = pd.read_csv(responses_path)
            
            # Trouver une colonne de texte
            for col in ['full_text', 'text', 'content', 'message', 'tweet']:
                if col in df.columns:
                    return df, col
            
            return df, None
        
        # Si aucun fichier n'est trouvé
        st.error("Aucun fichier de données trouvé")
        return pd.DataFrame(), None
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return pd.DataFrame(), None

# Charger les données
data, text_column = load_data()

if data.empty:
    st.error("Impossible de charger les données")
else:
    # Vérifier si une colonne de texte a été trouvée
    if text_column is None:
        # Créer des données de démonstration
        st.warning("Aucune colonne de texte trouvée dans les données. Utilisation de données de démonstration.")
        
        # Créer un ensemble de données fictives pour la démonstration
        demo_texts = [
            "Problème avec ma facture qui est beaucoup trop élevée ce mois-ci",
            "L'application ne fonctionne plus depuis la mise à jour",
            "Mon chauffage ne s'allume plus, besoin d'aide urgente",
            "Impossible de joindre le service client depuis 3 jours",
            "Le technicien n'est jamais venu pour l'installation",
            "La facturation est complètement erronée",
            "Je n'arrive pas à me connecter sur le site web",
            "Problème de température dans l'appartement",
            "Aucune réponse du service client malgré plusieurs relances",
            "Rendez-vous d'installation annulé sans prévenir"
        ]
        
        # Créer un DataFrame avec ces textes
        data = pd.DataFrame({
            'id': range(1, len(demo_texts) + 1),
            'text': demo_texts,
            'sentiment': [-0.5, -0.4, -0.6, -0.7, -0.5, -0.4, -0.3, -0.6, -0.7, -0.5]
        })
        
        text_column = 'text'
        
        # Ajouter une catégorie de sentiment
        data['sentiment_category'] = pd.cut(
            data['sentiment'],
            bins=[-1, -0.2, 0.2, 1],
            labels=['Négatif', 'Neutre', 'Positif']
        )
    
    # Si le sentiment n'est pas encore calculé
    if 'sentiment_category' not in data.columns:
        # Ajouter une analyse simplifiée des sentiments
        def simple_sentiment(text):
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
        
        data['sentiment'] = data[text_column].apply(simple_sentiment)
        data['sentiment_category'] = pd.cut(
            data['sentiment'],
            bins=[-1, -0.2, 0.2, 1],
            labels=['Négatif', 'Neutre', 'Positif']
        )
    
    # Filtrer les tweets négatifs et neutres
    filtered_data = data[data['sentiment_category'].isin(['Négatif', 'Neutre'])]
    
    # Calculer la catégorie de problème pour chaque tweet
    filtered_data['problem_category'] = filtered_data[text_column].apply(categorize_problem)
    
    # Statistiques des problèmes
    st.header("Analyse des types de problèmes")
    
    problem_counts = filtered_data['problem_category'].value_counts().reset_index()
    problem_counts.columns = ['Catégorie', 'Nombre']
    
    # Afficher côte à côte
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribution des problèmes")
        st.dataframe(problem_counts, use_container_width=True)
        
        st.markdown("### Légende des catégories")
        categories_explanation = {
            'Facturation': 'Problèmes liés aux factures, prélèvements, tarifs',
            'Application/Site': 'Problèmes avec l\'application mobile ou le site web',
            'Chauffage/Eau': 'Problèmes liés au chauffage ou à l\'eau chaude',
            'Service Client': 'Difficultés à joindre ou obtenir une réponse',
            'Installation': 'Problèmes avec les installations ou interventions',
            'Autre': 'Problèmes divers non classifiés'
        }
        
        for cat, desc in categories_explanation.items():
            st.write(f"- **{cat}**: {desc}")
    
    with col2:
        st.subheader("Graphique des problèmes")
        
        # Graphique en camembert
        fig = px.pie(
            problem_counts, 
            values='Nombre', 
            names='Catégorie',
            title="Répartition des types de problèmes",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            marker=dict(line=dict(color='white', width=2)),
            pull=[0.05 if x == problem_counts['Nombre'].max() else 0 for x in problem_counts['Nombre']]
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Afficher quelques exemples de tweets par catégorie
    st.header("Exemples par catégorie de problème")
    
    selected_category = st.selectbox(
        "Sélectionner une catégorie de problème",
        options=problem_counts['Catégorie'].tolist()
    )
    
    if selected_category:
        examples = filtered_data[filtered_data['problem_category'] == selected_category]
        if not examples.empty:
            st.subheader(f"Exemples de la catégorie: {selected_category}")
            
            # Limiter à 5 exemples maximum
            examples_to_show = min(5, len(examples))
            for i in range(examples_to_show):
                with st.expander(f"Exemple {i+1}"):
                    st.write(examples.iloc[i][text_column])
            
            # Option pour voir tous les exemples
            if st.button(f"Voir tous les exemples ({len(examples)} tweets)"):
                st.dataframe(examples[[text_column, 'sentiment_category']], use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Analyse des plaintes clients - Dashboard Engie") 
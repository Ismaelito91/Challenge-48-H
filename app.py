import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime, timedelta
import re
from textblob import TextBlob
import locale
import os

# Configuration de la page - DOIT ÊTRE PREMIER APPEL À STREAMLIT
st.set_page_config(
    page_title="Dashboard Service client de Engie",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importer les fonctions communes depuis utils.py
from utils import analyze_sentiment, categorize_problem, clean_tweet_text

# Tenter d'importer les fonctionnalités avancées
try:
    from agent_ia import analyze_tweet_advanced
    AGENT_IA_AVAILABLE = True
except ImportError:
    AGENT_IA_AVAILABLE = False

# Ajouter l'option d'utiliser l'agent IA avancé dans la barre latérale
st.sidebar.title("Options avancées")
use_advanced_ai = st.sidebar.checkbox("Utiliser l'analyse IA avancée", value=AGENT_IA_AVAILABLE)

# Titre de l'application
st.title("Dashboard Service client de Engie")
st.markdown("---")

# Définir les chemins des fichiers de données
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLEANED_TWEETS_PATH = os.path.join(BASE_DIR, 'cleaned_tweets.csv')
MODEL_RESPONSES_PATH = os.path.join(BASE_DIR, 'model_responses.csv')

# Fonction pour charger les données tweets
@st.cache_data
def load_tweets_data():
    try:
        # Vérifier si le fichier existe et afficher son chemin
        if os.path.exists(CLEANED_TWEETS_PATH):
            df = pd.read_csv(CLEANED_TWEETS_PATH, parse_dates=False)
            st.success(f"Fichier trouvé et chargé: {len(df)} tweets")
            
            # Convertir la colonne date en datetime
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            # Assurer que chaque tweet a un ID unique
            if 'id' in df.columns and df['id'].duplicated().any():
                df['original_id'] = df['id'].copy()
                df['id'] = df.index.astype(str) + '_' + df['id'].astype(str)
                
            return df
        else:
            st.error(f"Fichier {CLEANED_TWEETS_PATH} introuvable")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Erreur lors du chargement des tweets: {e}")
        return pd.DataFrame()

# Fonction simplifiée pour l'analyse des sentiments
def analyze_sentiment(text):
    # Si l'analyse avancée est activée et disponible
    if use_advanced_ai and AGENT_IA_AVAILABLE:
        try:
            return analyze_tweet_advanced(text)
        except Exception as e:
            st.warning(f"Erreur avec l'analyse avancée: {e}. Utilisation de l'analyse simplifiée.")
    
    # Version simplifiée qui classifie simplement en fonction de mots clés
    text = str(text).lower()
    
    # Nettoyer le texte si la fonction est disponible
    try:
        text = clean_tweet_text(text)
    except:
        pass  # Continuer sans nettoyage si la fonction n'est pas disponible
    
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

# Sidebar pour les filtres
st.sidebar.header("Filtres")

# Charger les données de tweets
tweets_df = load_tweets_data()

if not tweets_df.empty:
    # Filtre de date pour les tweets
    min_date = tweets_df['date'].min().date()
    max_date = tweets_df['date'].max().date()
    
    # Correction ici: définir une date de début et de fin par défaut
    start_date = min_date
    end_date = max_date
    
    # Utiliser le sélecteur de dates
    tweet_date_range = st.sidebar.date_input(
        "Sélectionner la période",
        value=(start_date, end_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Correction: vérifier si tweet_date_range est un tuple ou non
    if isinstance(tweet_date_range, tuple) and len(tweet_date_range) >= 2:
        start_date, end_date = tweet_date_range[0], tweet_date_range[1]
    else:
        # Si c'est une seule date, l'utiliser comme début et fin
        start_date = end_date = tweet_date_range
    
    # Filtrer les tweets par date
    tweets_filtered = tweets_df[
        (tweets_df['date'].dt.date >= start_date) & 
        (tweets_df['date'].dt.date <= end_date)
    ]
    
    # Analyser les sentiments
    tweets_filtered['sentiment'] = tweets_filtered['full_text'].apply(analyze_sentiment)
    tweets_filtered['sentiment_category'] = pd.cut(
        tweets_filtered['sentiment'],
        bins=[-1, -0.2, 0.2, 1],
        labels=['Négatif', 'Neutre', 'Positif']
    )
    
    # Métriques des tweets
    st.header("Analyse des tweets service client")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Nombre de tweets", 
            value=f"{len(tweets_filtered)}"
        )
    
    with col2:
        negative_pct = (tweets_filtered['sentiment_category'] == 'Négatif').mean() * 100
        st.metric(
            label="Tweets négatifs",
            value=f"{negative_pct:.1f}%"
        )
    
    with col3:
        neutral_pct = (tweets_filtered['sentiment_category'] == 'Neutre').mean() * 100
        st.metric(
            label="Tweets neutres",
            value=f"{neutral_pct:.1f}%"
        )
    
    with col4:
        positive_pct = (tweets_filtered['sentiment_category'] == 'Positif').mean() * 100
        st.metric(
            label="Tweets positifs",
            value=f"{positive_pct:.1f}%"
        )
    
    st.markdown("---")
    
    # Visualisations des tweets
    st.header("Visualisations des tweets")
    
    # Réduire à deux onglets maintenant que le troisième est une page séparée
    tab1, tab2 = st.tabs(["Analyse temporelle", "Analyse des sentiments"])
    
    with tab1:
        st.subheader("Évolution des tweets dans le temps")
        
        # Format plus lisible pour l'affichage des mois en français
        try:
            locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  # Pour Linux/Mac
        except:
            try:
                locale.setlocale(locale.LC_TIME, 'fra_fra')  # Pour Windows
            except:
                pass  # Si aucune locale française n'est disponible

        # Créer les colonnes pour la date et le tri
        tweets_filtered['year_month'] = tweets_filtered['date'].dt.strftime('%B %Y')
        tweets_filtered['sort_date'] = tweets_filtered['date'].dt.strftime('%Y-%m')
        
        # Regrouper par mois
        tweets_by_month = tweets_filtered.groupby('year_month').size().reset_index(name='count')
        
        # Ajouter la colonne de tri
        month_mapping = tweets_filtered[['year_month', 'sort_date']].drop_duplicates()
        tweets_by_month = tweets_by_month.merge(month_mapping, on='year_month', how='left')
        
        # Trier les données par la date de tri
        tweets_by_month = tweets_by_month.sort_values('sort_date')
        
        # Liste des mois dans le bon ordre
        month_order = tweets_by_month['year_month'].tolist()
        
        # Grouper par sentiment et mois
        sentiment_by_month = tweets_filtered.groupby(['year_month', 'sentiment_category']).size().reset_index(name='count')
        
        # Ajouter la colonne de tri
        sentiment_by_month = sentiment_by_month.merge(month_mapping, on='year_month', how='left')
        
        # Trier les données par sentiment
        sentiment_by_month = sentiment_by_month.sort_values('sort_date')
        
        # Option pour choisir le type de visualisation
        chart_type = st.radio("Type de visualisation", ["Simple", "Détaillée"], horizontal=True)
        
        if chart_type == "Simple":
            # Graphique à barres pour les mois
            fig = px.bar(
                tweets_by_month, 
                x='year_month', 
                y='count',
                title="Évolution mensuelle des tweets",
                color_discrete_sequence=["rgba(55, 83, 109, 0.7)"],
                category_orders={"year_month": month_order}
            )
            
            # Personnalisation du graphique
            fig.update_traces(
                marker_line_width=1,
                marker_line_color="rgb(25, 43, 79)",
                opacity=0.8,
                hovertemplate='<b>%{x}</b><br>Nombre de tweets: %{y}<extra></extra>'
            )
            
            fig.update_layout(
                xaxis_title="Mois",
                yaxis_title="Nombre de tweets",
                hovermode="x unified",  # Affiche toutes les valeurs pour un mois sur survol
                plot_bgcolor="rgba(240, 240, 240, 0.5)",  # Fond légèrement gris
                margin=dict(l=20, r=20, t=40, b=20),
                height=450,
            )
            
        else:  # Visualisation détaillée
            # Graphique à barres empilées par sentiment
            fig = px.bar(
                sentiment_by_month, 
                x='year_month', 
                y='count',
                color='sentiment_category',
                title="Évolution mensuelle des tweets par sentiment",
                barmode='stack',
                color_discrete_map={
                    'Négatif': 'rgba(231, 76, 60, 0.7)',
                    'Neutre': 'rgba(241, 196, 15, 0.7)',
                    'Positif': 'rgba(46, 204, 113, 0.7)'
                },
                category_orders={"year_month": month_order}
            )
            
            # Personnalisation du graphique
            fig.update_traces(
                marker_line_width=1,
                marker_line_color="white",
                opacity=0.9,
                hovertemplate='<b>%{x}</b><br>Sentiment: %{fullData.name}<br>Nombre de tweets: %{y}<extra></extra>'
            )
            
            fig.update_layout(
                xaxis_title="Mois",
                yaxis_title="Nombre de tweets",
                legend_title="Sentiment",
                hovermode="x unified",
                plot_bgcolor="rgba(240, 240, 240, 0.5)",
                margin=dict(l=20, r=20, t=40, b=20),
                height=450,
            )
        
        # Ajouter des annotations pour le mois le plus important
        highest_month = tweets_by_month.iloc[tweets_by_month['count'].argmax()]
        fig.add_annotation(
            x=highest_month['year_month'],
            y=highest_month['count'],
            text=f"Pic: {highest_month['count']} tweets",
            showarrow=True,
            arrowhead=2,
            arrowcolor="black",
            arrowsize=1,
            arrowwidth=1,
            yshift=10
        )
        
        # Afficher le graphique
        st.plotly_chart(fig, use_container_width=True)
        
        # Ajouter des statistiques en dessous du graphique
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_tweets = tweets_by_month['count'].mean()
            st.metric("Moyenne par mois", f"{avg_tweets:.1f} tweets")
        with col2:
            max_tweets = tweets_by_month['count'].max()
            st.metric("Maximum mensuel", f"{max_tweets} tweets")
        with col3:
            total_months = len(tweets_by_month)
            st.metric("Nombre de mois", f"{total_months}")
    
    with tab2:
        st.subheader("Répartition des sentiments")
        sentiment_counts = tweets_filtered['sentiment_category'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Nombre']
        
        # Définir une palette de couleurs cohérente pour tous les graphiques
        sentiment_colors = {
            'Négatif': 'rgba(231, 76, 60, 0.7)',
            'Neutre': 'rgba(241, 196, 15, 0.7)',
            'Positif': 'rgba(46, 204, 113, 0.7)'
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                sentiment_counts, 
                values='Nombre', 
                names='Sentiment',
                title="Répartition des sentiments",
                color='Sentiment',
                color_discrete_map=sentiment_colors
            )
            # Amélioration de l'apparence du graphique
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                marker=dict(line=dict(color='white', width=2)),
                hovertemplate='<b>%{label}</b><br>Nombre: %{value}<br>Pourcentage: %{percent}<extra></extra>'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                sentiment_counts,
                x='Sentiment',
                y='Nombre',
                title="Nombre de tweets par sentiment",
                color='Sentiment',
                color_discrete_map=sentiment_colors
            )
            # Amélioration de l'apparence du graphique
            fig.update_traces(
                marker_line_width=1,
                marker_line_color="white",
                opacity=0.8,
                hovertemplate='<b>%{x}</b><br>Nombre de tweets: %{y}<extra></extra>'
            )
            fig.update_layout(
                xaxis_title="Sentiment",
                yaxis_title="Nombre de tweets",
                plot_bgcolor="rgba(240, 240, 240, 0.5)",
                margin=dict(l=20, r=20, t=40, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Afficher les tweets filtrés
    st.header("Tweets filtrés")
    
    # Filtrage par sentiment
    sentiment_filter = st.multiselect(
        "Filtrer par sentiment",
        options=tweets_filtered['sentiment_category'].unique(),
        default=tweets_filtered['sentiment_category'].unique()
    )
    
    if sentiment_filter:
        display_tweets = tweets_filtered[tweets_filtered['sentiment_category'].isin(sentiment_filter)]
        
        # Créer une copie du dataframe pour la modification
        display_df = display_tweets.copy()
        
        # Formater les dates (sans l'heure)
        display_df['date'] = display_tweets['date'].dt.strftime('%d/%m/%Y')
        
        # Ajouter une colonne d'index unique pour distinguer les lignes avec le même ID Twitter
        display_df = display_df.reset_index().rename(columns={'index': 'row_id'})
        
        # Identifier les IDs en double
        duplicate_ids = display_df['id'].duplicated(keep=False)
        display_df['id_status'] = 'unique'
        display_df.loc[duplicate_ids, 'id_status'] = 'doublon'
        
        # Ajouter cette ligne pour formater les ID de manière plus lisible
        display_df['id_formatted'] = display_df.apply(
            lambda row: f"#{row['row_id']} (ID: {str(row['original_id']) if 'original_id' in display_df.columns else row['id']})",
            axis=1
        )
        
        # Puis utiliser cette colonne dans l'affichage
        st.dataframe(
            display_df[['id_formatted', 'date', 'screen_name', 'full_text', 'sentiment_category']],
            use_container_width=True
        )
        
        # Téléchargement des tweets filtrés
        st.download_button(
            label="Télécharger les tweets filtrés (CSV)",
            data=display_tweets.to_csv(index=False).encode('utf-8'),
            file_name=f"tweets_filtered_{start_date}_to_{end_date}.csv",
            mime="text/csv"
        )
    else:
        st.write("Aucun sentiment sélectionné.")

else:
    st.error("Impossible de charger les données des tweets. Veuillez vérifier le fichier CSV.")

# Footer avec lien vers la page des plaintes
st.markdown("---")
st.markdown("Dashboard créé avec Streamlit")
st.markdown("Pour une analyse détaillée des plaintes, consultez l'onglet 'Analyse des plaintes' dans le menu de gauche.") 
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime, timedelta
import re
from textblob import TextBlob

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Service client de Engie",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre de l'application
st.title("Dashboard Service client de Engie")
st.markdown("---")

# Fonction pour charger les données tweets
@st.cache_data
def load_tweets_data():
    try:
        df = pd.read_csv('cleaned_tweets.csv')
        # Convertir date en datetime si ce n'est pas déjà fait
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des tweets: {e}")
        # Retourner un DataFrame vide en cas d'erreur
        return pd.DataFrame()

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
    
    tab1, tab2 = st.tabs(["Analyse temporelle", "Analyse des sentiments"])
    
    with tab1:
        st.subheader("Évolution des tweets dans le temps")
        
        # Créer une colonne pour le mois
        tweets_filtered['year'] = tweets_filtered['date'].dt.year
        tweets_filtered['month'] = tweets_filtered['date'].dt.month
        tweets_filtered['year_month'] = tweets_filtered['date'].dt.strftime('%Y-%m')
        
        # Regrouper par mois au lieu de par trimestre
        tweets_by_month = tweets_filtered.groupby('year_month').size().reset_index(name='count')
        
        # Créer aussi des groupes par sentiment pour un graphique plus riche
        sentiment_by_month = tweets_filtered.groupby(['year_month', 'sentiment_category']).size().reset_index(name='count')
        
        # Option pour choisir le type de visualisation
        chart_type = st.radio("Type de visualisation", ["Simple", "Détaillée"], horizontal=True)
        
        if chart_type == "Simple":
            # Graphique à barres pour les mois
            fig = px.bar(
                tweets_by_month, 
                x='year_month', 
                y='count',
                title="Évolution mensuelle des tweets",
                color_discrete_sequence=["rgba(55, 83, 109, 0.7)"],  # Bleu foncé avec transparence
            )
            
            # Personnalisation du graphique
            fig.update_traces(
                marker_line_width=1,
                marker_line_color="rgb(25, 43, 79)",
                opacity=0.8
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
            # Graphique à barres groupées par sentiment
            fig = px.bar(
                sentiment_by_month, 
                x='year_month', 
                y='count',
                color='sentiment_category',
                title="Évolution mensuelle des tweets par sentiment",
                barmode='group',  # Barres groupées
                color_discrete_map={
                    'Négatif': 'rgba(231, 76, 60, 0.7)',
                    'Neutre': 'rgba(241, 196, 15, 0.7)',
                    'Positif': 'rgba(46, 204, 113, 0.7)'
                },
            )
            
            # Personnalisation du graphique
            fig.update_traces(
                marker_line_width=1,
                opacity=0.8
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
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                sentiment_counts, 
                values='Nombre', 
                names='Sentiment',
                title="Répartition des sentiments"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                sentiment_counts,
                x='Sentiment',
                y='Nombre',
                title="Nombre de tweets par sentiment"
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
        
        # Afficher un tableau interactif avec les IDs ajoutés
        st.dataframe(
            display_tweets[['id', 'date', 'screen_name', 'full_text', 'sentiment_category']],
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

# Footer
st.markdown("---")
st.markdown("Dashboard créé avec Streamlit")

# Ajouter cette fonction après la fonction analyze_sentiment
def categorize_problem(text):
    """Catégorise le type de problème mentionné dans un tweet négatif"""
    text = str(text).lower()
    
    # Définir les mots-clés pour chaque catégorie de problème
    categories = {
        'Facturation': ['facture', 'mensualité', 'prélèvement', 'payer', 'payé', 'tarif', 'prix', 'coût', 'cher', 'euro', '€'],
        'Application/Site': ['appli', 'application', 'site', 'bug', 'connexion', 'connecter', 'monpilotageelec', 'espace client'],
        'Chauffage/Eau': ['chauffage', 'eau chaude', 'chaudière', 'température', 'froid', 'chaleur', 'douche', 'radiateur'],
        'Service Client': ['service client', 'joindre', 'appeler', 'rappeler', 'téléphone', 'contact', 'réponse', 'mail', 'message'],
        'Installation': ['technicien', 'intervention', 'installateur', 'installer', 'dépanner', 'réparation', 'panne', 'compteur']
    }
    
    # Déterminer la catégorie en fonction des mots-clés présents
    scores = {cat: 0 for cat in categories}
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in text:
                scores[category] += 1
    
    # Si aucune catégorie n'est trouvée
    if max(scores.values(), default=0) == 0:
        return "Autre"
    
    # Retourner la catégorie avec le score le plus élevé
    return max(scores.items(), key=lambda x: x[1])[0] 
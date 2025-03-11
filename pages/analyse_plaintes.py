import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
import numpy as np
import locale
import matplotlib.pyplot as plt
import matplotlib

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
        # Utiliser des valeurs par défaut plutôt qu'une analyse
        data['sentiment'] = -0.5  # Valeur par défaut négative
        data['sentiment_category'] = 'Négatif'  # Par défaut, considérer comme négatif
    
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
    
    # Répartition proportionnelle des problèmes par mois
    st.header("Évolution mensuelle des types de problèmes")

    # Vérifier si les données contiennent une colonne date
    if 'date' in filtered_data.columns:
        # Essayer de convertir la colonne date en datetime si ce n'est pas déjà fait
        try:
            # Vérifier si la conversion est nécessaire
            if not pd.api.types.is_datetime64_any_dtype(filtered_data['date']):
                filtered_data['date'] = pd.to_datetime(filtered_data['date'], errors='coerce')
            
            # Vérifier s'il reste des dates valides après conversion
            if filtered_data['date'].notna().sum() > 0:
                # Créer une fonction de mappage des mois en français
                def get_french_month_name(month_num):
                    month_names = {
                        '01': 'Janvier', '02': 'Février', '03': 'Mars', '04': 'Avril',
                        '05': 'Mai', '06': 'Juin', '07': 'Juillet', '08': 'Août',
                        '09': 'Septembre', '10': 'Octobre', '11': 'Novembre', '12': 'Décembre'
                    }
                    return month_names.get(month_num, month_num)

                # Créer un ordre numérique pour trier correctement les mois
                filtered_data['month_sort'] = filtered_data['date'].dt.strftime('%Y%m')
                
                # Extraire le mois et l'année séparément
                filtered_data['month_num'] = filtered_data['date'].dt.strftime('%m')
                filtered_data['year'] = filtered_data['date'].dt.strftime('%Y')
                
                # Créer une colonne avec un format plus lisible pour l'affichage
                filtered_data['month_name'] = filtered_data['month_num'].apply(get_french_month_name) + ' ' + filtered_data['year']
                
                # Grouper par mois et catégorie de problème
                problems_by_month = filtered_data.groupby(['month_sort', 'month_name', 'problem_category']).size().reset_index(name='count')
                
                # Trier par année et mois (ordre chronologique)
                problems_by_month = problems_by_month.sort_values('month_sort')
                
                # Récupérer l'ordre des mois pour l'affichage
                month_order = problems_by_month['month_name'].unique()
                
                # Vérifier qu'il y a des données à afficher
                if not problems_by_month.empty:
                    # Normaliser explicitement les données à 100%
                    # Calculer le total par mois
                    total_by_month = problems_by_month.groupby('month_name')['count'].sum().reset_index()
                    
                    # Fusionner avec les données d'origine
                    problems_by_month = problems_by_month.merge(total_by_month, on='month_name', suffixes=('', '_total'))
                    
                    # Calculer le pourcentage
                    problems_by_month['percentage'] = problems_by_month['count'] / problems_by_month['count_total'] * 100
                    
                    # Créer le graphique avec les pourcentages calculés
                    fig = px.bar(
                        problems_by_month, 
                        x='month_name', 
                        y='percentage',  # Utiliser directement les pourcentages calculés
                        color='problem_category',
                        title="Répartition des types de problèmes par mois (base 100)",
                        category_orders={"month_name": month_order},
                        color_discrete_sequence=px.colors.qualitative.Bold,
                        labels={"month_name": "Mois", "percentage": "Pourcentage (%)", "problem_category": "Type de problème"}
                    )
                    
                    # Configurer le graphique pour l'empilement standard
                    fig.update_layout(
                        barmode='stack',  # Empiler les barres
                        xaxis_title="Mois",
                        yaxis_title="Pourcentage (%)",
                        legend_title="Type de problème",
                        hovermode="x unified",
                        yaxis=dict(range=[0, 100]),  # Forcer l'échelle Y de 0 à 100%
                        plot_bgcolor="rgba(240, 240, 240, 0.5)",
                        margin=dict(l=20, r=20, t=40, b=20),
                        height=500
                    )
                    
                    # Améliorer l'apparence du graphique
                    fig.update_traces(
                        marker_line_width=1,
                        marker_line_color="white",
                        opacity=0.8,
                        hovertemplate='<b>%{x}</b><br>Type: %{fullData.name}<br>Pourcentage: %{y:.1f}%<extra></extra>'
                    )
                    
                    # Afficher le graphique
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Pas assez de données pour afficher une répartition par mois.")
            else:
                st.warning("Aucune date valide trouvée après conversion.")
        except Exception as e:
            st.error(f"Erreur lors de l'analyse temporelle: {e}")
            
            # Alternative: créer un exemple pour démonstration avec des dates fictives
            st.info("Génération d'un exemple de démonstration avec des dates fictives...")
            
            # Créer des données de démonstration pour le graphique mensuel
            demo_months = ['Janvier 2023', 'Février 2023', 'Mars 2023', 'Avril 2023', 'Mai 2023', 'Juin 2023']
            categories = ['Facturation', 'Application/Site', 'Chauffage/Eau', 'Service Client', 'Installation', 'Autre']
            
            # Créer un DataFrame de démonstration
            demo_data = []
            for month in demo_months:
                for category in categories:
                    # Générer un nombre aléatoire pour chaque catégorie et mois
                    count = np.random.randint(5, 30)
                    demo_data.append({
                        'month_name': month,
                        'problem_category': category,
                        'count': count
                    })
            
            demo_df = pd.DataFrame(demo_data)
            
            # Créer le graphique de démonstration
            fig = px.bar(
                demo_df, 
                x='month_name', 
                y='count',
                color='problem_category',
                title="DÉMONSTRATION - Évolution mensuelle des types de problèmes",
                category_orders={"month_name": demo_months},
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
            fig.update_layout(
                barmode='stack',
                xaxis_title="Mois",
                yaxis_title="Nombre de problèmes",
                legend_title="Type de problème"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Note: Ce graphique est une démonstration avec des données fictives")
    else:
        # Créer des données de démonstration avec dates fictives
        st.info("Les données ne contiennent pas d'information de date. Affichage d'un exemple avec des données fictives.")
        
        # Code pour générer un exemple similaire à celui ci-dessus

# Footer
st.markdown("---")
st.markdown("Analyse des plaintes clients - Dashboard Engie") 
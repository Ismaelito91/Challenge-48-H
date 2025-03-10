import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Interactif",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre de l'application
st.title("Dashboard Interactif")
st.markdown("---")

# Sidebar pour les filtres
st.sidebar.header("Filtres")
date_range = st.sidebar.date_input(
    "Sélectionner la période",
    value=(datetime(2023, 1, 1), datetime(2023, 12, 31))
)

# Génération de données aléatoires pour l'exemple
def generate_sample_data():
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    categories = ['Catégorie A', 'Catégorie B', 'Catégorie C', 'Catégorie D']
    
    data = {
        'Date': np.random.choice(dates, 1000),
        'Catégorie': np.random.choice(categories, 1000),
        'Valeur': np.random.randint(100, 10000, 1000),
        'Quantité': np.random.randint(1, 100, 1000)
    }
    
    return pd.DataFrame(data)

# Chargement des données
@st.cache_data
def load_data():
    # Dans un cas réel, vous chargeriez vos données depuis un fichier CSV ou une base de données
    # Par exemple: df = pd.read_csv('data/sample_data.csv')
    # Pour cet exemple, nous générons des données aléatoires
    return generate_sample_data()

df = load_data()

# Filtrage des données selon la période sélectionnée
df_filtered = df[(df['Date'] >= pd.Timestamp(date_range[0])) & 
                (df['Date'] <= pd.Timestamp(date_range[1]))]

# Affichage des métriques clés
st.header("Métriques clés")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total des ventes", 
              value=f"{df_filtered['Valeur'].sum():,.0f} €", 
              delta=f"{df_filtered['Valeur'].sum() / df['Valeur'].sum() * 100:.1f}%")

with col2:
    st.metric(label="Quantité vendue", 
              value=f"{df_filtered['Quantité'].sum():,d}")

with col3:
    st.metric(label="Panier moyen", 
              value=f"{df_filtered['Valeur'].mean():,.0f} €")

with col4:
    st.metric(label="Nombre de transactions", 
              value=f"{len(df_filtered):,d}")

st.markdown("---")

# Visualisations
st.header("Visualisations")

# Onglets pour différentes visualisations
tab1, tab2, tab3 = st.tabs(["Évolution temporelle", "Par catégorie", "Distribution"])

with tab1:
    st.subheader("Évolution des ventes")
    df_time = df_filtered.groupby(df_filtered['Date'].dt.to_period('M')).agg({'Valeur': 'sum'}).reset_index()
    df_time['Date'] = df_time['Date'].dt.to_timestamp()
    
    fig = px.line(df_time, x='Date', y='Valeur', title="Évolution mensuelle des ventes")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Répartition par catégorie")
    df_cat = df_filtered.groupby('Catégorie').agg({'Valeur': 'sum'}).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(df_cat, values='Valeur', names='Catégorie', title="Répartition des ventes par catégorie")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(df_cat, x='Catégorie', y='Valeur', title="Ventes par catégorie")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Distribution des ventes")
    fig = px.histogram(df_filtered, x='Valeur', nbins=50, title="Distribution des valeurs de vente")
    st.plotly_chart(fig, use_container_width=True)

# Filtrage interactif supplémentaire
st.header("Filtrage interactif")

category_filter = st.multiselect(
    "Filtrer par catégorie",
    options=df['Catégorie'].unique(),
    default=df['Catégorie'].unique()
)

if category_filter:
    filtered_data = df_filtered[df_filtered['Catégorie'].isin(category_filter)]
    st.dataframe(filtered_data, use_container_width=True)
else:
    st.dataframe(df_filtered, use_container_width=True)

# Téléchargement des données
st.download_button(
    label="Télécharger les données filtrées (CSV)",
    data=df_filtered.to_csv(index=False).encode('utf-8'),
    file_name=f"dashboard_data_{date_range[0]}_to_{date_range[1]}.csv",
    mime="text/csv"
)

# Footer
st.markdown("---")
st.markdown("Dashboard créé avec Streamlit") 
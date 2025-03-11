# Challenge-48-H: Dashboard d'analyse du service client Engie

## Description

Ce projet est un dashboard interactif développé avec Streamlit pour analyser les tweets et les plaintes des clients d'Engie. Il permet de visualiser les tendances, d'analyser les sentiments et de catégoriser les problèmes rencontrés par les clients.

## Technologies utilisées

- Python
- Streamlit
- Pandas
- Plotly
- NLTK
- TextBlob
- WordCloud
- Mistral AI (pour l'analyse avancée)

## Prérequis

- Python 3.8 ou supérieur
- Pip (gestionnaire de paquets Python)
- Git (optionnel, pour cloner le dépôt)

## Installation

### 1. Cloner le projet (ou télécharger le zip)

```bash
git clone https://github.com/votre-username/Challenge-48-H.git
cd Challenge-48-H
```

### 2. Créer un environnement virtuel (recommandé)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Installation détaillée des dépendances

Si l'installation via requirements.txt échoue, voici la liste complète des bibliothèques à installer manuellement :

```bash
pip install streamlit
pip install pandas
pip install numpy
pip install matplotlib
pip install plotly
pip install nltk
pip install textblob
pip install wordcloud
pip install mistralai  # Pour l'API Mistral
```

### 5. Télécharger les ressources NLTK nécessaires

```bash
python download_nltk.py
```

### 6. Configuration API Mistral (optionnel)

Si vous souhaitez utiliser les fonctionnalités d'analyse avancée :

1. Créez un compte sur [Mistral AI](https://mistral.ai)
2. Obtenez une clé API
3. Remplacez la clé API dans le fichier `agent_ia.py`

## Données requises

Pour fonctionner correctement, l'application nécessite les fichiers suivants placés à la racine du projet:

- `cleaned_tweets.csv` : Données de tweets nettoyées
- `model_responses.csv` : Réponses du modèle d'analyse (généré par agent_ia.py)

## Utilisation

```bash
streamlit run app.py
```

L'application sera accessible dans votre navigateur à l'adresse `http://localhost:8501`.

## Fonctionnalités

1. **Dashboard principal** (app.py)

   - Affichage des métriques clés (nombre de tweets, pourcentages par sentiment)
   - Analyse temporelle des tweets
   - Visualisation de la répartition des sentiments
   - Liste des tweets filtrables

2. **Analyse des plaintes** (pages/analyse_plaintes.py)
   - Répartition des types de problèmes
   - Évolution mensuelle des problèmes
   - Visualisation des mots-clés les plus utilisés
   - Affichage des tweets les plus positifs et les plus négatifs

## Structure du projet

- `app.py` : Point d'entrée principal de l'application
- `pages/analyse_plaintes.py` : Page d'analyse détaillée des types de plaintes
- `utils.py` : Fonctions utilitaires partagées entre différents modules
- `agent_ia.py` : Module d'analyse avancée des tweets via l'API Mistral
- `download_nltk.py` : Script pour télécharger les ressources NLTK nécessaires
- `requirements.txt` : Liste des dépendances Python

## Note sur les données

Si les fichiers de données (`cleaned_tweets.csv` et `model_responses.csv`) ne sont pas disponibles, l'application générera des données de démonstration pour illustrer les fonctionnalités.

## Dépannage

### Problème d'importation de module

Si vous rencontrez l'erreur `ModuleNotFoundError`, vérifiez que toutes les dépendances sont installées:

```bash
pip install -r requirements.txt
```

### Messages du terminal

Si vous voyez des messages dans votre terminal lors du lancement de l'application, c'est normal. L'application utilise `agent_ia.py` qui peut afficher des logs lors de son initialisation.

### Erreurs de locale

Si vous rencontrez des erreurs liées aux paramètres régionaux (locale) sur Linux/macOS, essayez de définir la variable d'environnement:

```bash
export LC_ALL=fr_FR.UTF-8
export LANG=fr_FR.UTF-8
```

Sur Windows:

```bash
set LC_ALL=fra_fra
```

## Personnalisation

Pour modifier les catégories de problèmes ou les mots-clés associés, éditez la fonction `categorize_problem` dans le fichier `utils.py`.

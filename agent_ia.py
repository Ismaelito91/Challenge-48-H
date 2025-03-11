import json
import csv
import time  # Importation du module time
from datetime import datetime
from mistralai import Mistral

api_key = "Hs0BhW1vJsSKYV41n7QNkFiZNOnTAjcQ"
model = "mistral-large-2411"
client = Mistral(api_key=api_key)

# Ouvrir le fichier CSV et lire son contenu
with open('cleaned_tweets.csv', newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    tweets_data = [row for row in csv_reader]

def process_tweet(tweet_index):
    if 1 <= tweet_index <= len(tweets_data):
        selected_tweet = tweets_data[tweet_index - 1]
        tweet_date = selected_tweet[4]  # Date en 5e colonne
        content = selected_tweet[3]  # Contenu en 4e colonne

        # Conversion de la date
        try:
            timestamp = float(tweet_date)
            tweet_date = datetime.utcfromtimestamp(timestamp / 1000).strftime("%Y-%m-%d")
        except ValueError:
            tweet_date = str(tweet_date)

        message = [
        {"role": "system", "content": "Tu vas recevoir des tweets de plainte et répondre toujours dans le format suivant :"
                                      "1. Tu vas devoir les noter de 0 à 100, 100 étant la situation la plus grave et 0 la situation la moins grave."
                                      "2. Si le sentiment de l'utilisateur est plus positif, neutre ou négatif envers ENGIE. Réponds juste par positif, neutre ou négatif."
                                      "3. Répartir les différrents tweet dans les catégories suivantes :Problème de facturation OU Panne et urgences OU Service client injoignable OU Probleme avec l'application OU Delai d'intervention OU Problème d'age..."
                                      "4. Si aucune catégorie n’est présente, crée une nouvelle catégorie basée sur le contenu du tweet."},
        {"role": "user", "content": content}
    ]
        
        chat_response = client.chat.complete(model=model, messages=message)
        model_response = chat_response.choices[0].message.content

        # Extraction des résultats
        score = None
        sentiment = "inconnu"
        category = "autre"

        try:
            score_line = [line for line in model_response.splitlines() if "Note" in line]
            if score_line:
                score = int(score_line[0].split(":")[1].strip())
        except (IndexError, ValueError):
            score = None

        # Gérer l'IndexError pour le sentiment
        try:
            sentiment_line = [line for line in model_response.splitlines() if any(s in line for s in ["positif", "neutre", "négatif"])]
            if sentiment_line:
                sentiment = sentiment_line[0].split(":")[1].strip().lower()
        except IndexError:
            # Si une erreur se produit, on ignore et laisse le sentiment à "inconnu"
            sentiment = "inconnu"

        try:
            category_line = [line for line in model_response.splitlines() if any(c in line for c in [
                "Problème de facturation", "Panne et urgences", "Service client injoignable", "Problème avec l'application", "Délai d'intervention", "Problème d'âge"])]
            if category_line:
                category = category_line[0].split(":")[1].strip().lower()
            else:
                category = model_response.splitlines()[-1]
        except IndexError:
            category = "autre"

        # Écriture immédiate dans le CSV
        try:
            with open('model_responses.csv', mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                next_id = sum(1 for row in reader) + 1
        except FileNotFoundError:
            next_id = 1

        output_data = {"ID": next_id, "date": tweet_date, "score": score, "sentiment": sentiment, "category": category}
        with open('model_responses.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["ID", "date", "score", "sentiment", "category"])
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(output_data)

        print(f"\nTweet traité : ID {next_id}, Date: {tweet_date}, Score: {score}, Sentiment: {sentiment}, Catégorie: {category}")

# Processus automatisé avec une requête par seconde
for i in range(1, len(tweets_data) + 1):
    process_tweet(i)
    time.sleep(4)  # Attente d'une seconde entre chaque requête

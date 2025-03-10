import json
import csv
from mistralai import Mistral

api_key = "Hs0BhW1vJsSKYV41n7QNkFiZNOnTAjcQ"
model = "mistral-large-2411"

client = Mistral(api_key=api_key)

# Open the CSV file and read its content
with open('cleaned_tweets.csv', newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    tweets = [row[3] for row in csv_reader]

# Use the 289 tweet as content for the example
content = tweets[89] if tweets else ""

# Prompt the user with a system message and the content of the tweet
message = [
    {"role": "system", "content": "Tu vas recevoir des tweets de plainte et répondre toujours dans le format suivant :"
                                  "1. Tu vas devoir les noter de 0 à 100, 100 étant la situation la plus grave et 0 la situation la moins grave."
                                  "2. Si le sentiment de l'utilisateur est plus positif, neutre ou négatif envers ENGIE. Réponds juste par positif, neutre ou négatif."
                                  "3. Répartir les différrents tweet dans les catégories suivants :Problème de facturation, Panne et urgences, Service client injoignable, Probleme avec l'aplication, Delai d'intervention,  Problème d'age, Autre."
                                  "4. Petit description de la situation."},
    {"role": "user","content": content}
]

# Get the model's response
chat_response = client.chat.complete(
    model=model,
    messages=message,
)

# Extract the content of the model's response
model_response = chat_response.choices[0].message.content

print(model_response)
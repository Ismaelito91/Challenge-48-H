import json
import csv
from datetime import datetime
from mistralai import Mistral

api_key = "Hs0BhW1vJsSKYV41n7QNkFiZNOnTAjcQ"
model = "mistral-large-2411"

client = Mistral(api_key=api_key)

# Open the CSV file and read its content
with open('cleaned_tweets.csv', newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    tweets_data = [row for row in csv_reader]

# Ask user for tweet number to process
tweet_index = int(input(f"Enter the tweet number to process (1 to {len(tweets_data)}): "))

# Ensure the input is within the valid range
if 1 <= tweet_index <= len(tweets_data):
    # Get the selected tweet data
    selected_tweet = tweets_data[tweet_index - 1]
    tweet_date = selected_tweet[4]  # Date is in the 5th column (index 4)
    content = selected_tweet[3]  # Content is in the 4th column

    # Convert the date from scientific notation (timestamp) to a readable date format
    try:
        # If the date is in scientific notation (timestamp), convert it
        timestamp = float(tweet_date)  # Convert to float to handle scientific notation
        tweet_date = datetime.utcfromtimestamp(timestamp / 1000).strftime("%Y-%m-%d")  # Only the date (no time)
    except ValueError:
        tweet_date = str(tweet_date)  # In case it's already in a readable format

    # Prompt the model with a system message and the content of the tweet
    message = [
        {"role": "system", "content": "Tu vas recevoir des tweets de plainte et répondre toujours dans le format suivant :"
                                      "1. Tu vas devoir les noter de 0 à 100, 100 étant la situation la plus grave et 0 la situation la moins grave."
                                      "2. Si le sentiment de l'utilisateur est plus positif, neutre ou négatif envers ENGIE. Réponds juste par positif, neutre ou négatif."
                                      "3. Répartir les différrents tweet dans les catégories suivants :Problème de facturation, Panne et urgences, Service client injoignable, Probleme avec l'application, Delai d'intervention, Problème d'age..."
                                      "4. Si aucune catégorie n’est présente, crée une nouvelle catégorie basée sur le contenu du tweet."},
        {"role": "user", "content": content}
    ]

    # Get the model's response
    chat_response = client.chat.complete(
        model=model,
        messages=message,
    )

    # Extract the content of the model's response
    model_response = chat_response.choices[0].message.content

    # Initialize output variables
    score = None
    sentiment = "inconnu"
    category = "autre"

    # Extract score from the model's response
    try:
        score_line = [line for line in model_response.splitlines() if "Note" in line]
        if score_line:
            score = int(score_line[0].split(":")[1].strip())  # Extract score and ensure it's an integer
    except (IndexError, ValueError):
        score = None  # In case of invalid extraction

    # Extract sentiment (looking for positive, neutral, or negative sentiment)
    sentiment_line = [line for line in model_response.splitlines() if "positif" in line or "neutre" in line or "négatif" in line]
    if sentiment_line:
        sentiment = sentiment_line[0].split(":")[1].strip().lower()  # Extract and clean sentiment

    # Extract category from the model's response and clean the category name
    category_line = [line for line in model_response.splitlines() if "Problème de facturation" in line or 
                     "Panne et urgences" in line or "Service client injoignable" in line or 
                     "Problème avec l'application" in line or "Délai d'intervention" in line or 
                     "Problème d'âge" in line]

    # Check if any predefined category is found
    if category_line:
        category = category_line[0].split(":")[1].strip().lower()  # Extract and clean the category
    else:
        # If no predefined category is found, let Mistral create a new category based on the tweet's content
        category = model_response.splitlines()[-1]  # Assuming the last line might contain the new category info

    # Calculate the next ID by checking the number of rows in the CSV
    try:
        with open('model_responses.csv', mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            next_id = sum(1 for row in reader) + 1  # Get the next ID by counting rows
    except FileNotFoundError:
        next_id = 1  # If file does not exist, start from ID 1

    # Prepare the output record with the generated ID
    output_data = {
        "ID": next_id,
        "date": tweet_date,
        "score": score,
        "sentiment": sentiment,
        "category": category
    }

    # Open the CSV file in append mode ('a') to add new data without overwriting
    with open('model_responses.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["ID", "date", "score", "sentiment", "category"])

        # If the file is empty, write the header (first row)
        file.seek(0, 2)  # Move to the end of the file
        if file.tell() == 0:
            writer.writeheader()  # Write header only if file is empty

        # Write the new data row
        writer.writerow(output_data)

    # Display the results
    print(f"\nProcessed Tweet:")
    print(f"ID: {next_id}")
    print(f"Date: {tweet_date}")
    print(f"Content: {content}")
    print(f"Score: {score}")
    print(f"Sentiment: {sentiment}")
    print(f"Category: {category}")

    print("\nModel responses appended to 'model_responses.csv'.")
else:
    print(f"Invalid tweet number. Please choose a number between 1 and {len(tweets_data)}.")

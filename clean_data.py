import pandas as pd
import emoji



# Charger les données
def load_data(file_path):
    df = pd.read_csv(file_path, sep=';', encoding='utf-8')
    return df


#  Fonction pour supprimer les emojis
def remove_emojis(text):
    if isinstance(text, str):
        return emoji.replace_emoji(text,replace='')
    return text


# Supprimer les guillemets
def remove_quotes(text):
    if isinstance(text, str):
        return text.replace('"', '').replace("'", '')
    return text

def clean_text(df):
    df['name'] = df['name'].apply(remove_emojis)
    df['full_text'] = df['full_text'].apply(remove_emojis).apply(remove_quotes)
    df['name'] = df['name'].where(df['name'].notna() & df['name'].str.strip().ne(''), df['screen_name'])
    return df

def process_dates(df):
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce', utc=True)
    df['date'] = df['created_at'].dt.strftime('%Y-%m-%d')
    df = df.drop(columns=['created_at'])
    return df

def process_ids(df):
    if 'id' in df.columns:
        df['id'] = df['id'].astype(str).str.replace(',', '.').astype(float, errors='ignore')
        df['id'] = df['id'].apply(lambda x: f"{x:.2E}" if pd.notna(x) else x)
    return df


def test_data(file_path):
    df = load_data(file_path)
    df = clean_text(df)
    df=process_ids(df)
    df = process_dates(df)
    return df


if __name__ == "__main__":
    file_path = "filtered_tweets_engie.csv"
    df_cleaned = test_data(file_path)
    df_cleaned.to_csv("cleaned_tweets.csv", index=False)

import json
import requests
from datetime import datetime
import re

#def fetch_newsapi_data(api_key, countries=['us', 'gb'], categories=['technology', 'business', 'science', 'health', 'sports']):
def fetch_newsapi_data(api_key, countries=['us'], categories=['technology', 'business']):
    """
    Fetches top headlines from NewsAPI for multiple countries and categories.
    """
    url = "https://newsapi.org/v2/top-headlines"
    all_articles = []
    
    for country in countries:
        for category in categories:
            params = {
                'apiKey': api_key,
                'country': country,
                'category': category,
                'pageSize': 100
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            articles = data.get("articles", [])
            
            for article in articles:
                article['country'] = country
                article['category'] = category
                article['ingestion_timestamp'] = datetime.utcnow().isoformat()
                all_articles.append(article)
    
    return all_articles


def save_to_local(data, filepath='/tmp/news_data.json'):
    articles = data if isinstance(data, list) else data.get('articles', [])
    
    with open(filepath, 'w') as f:
        for article in articles:
            clean_article = truncate_fields(article)
            json.dump(clean_article, f)
            f.write('\n')
    
    return filepath



def limit_sentences(text, max_sentences=5):
    """Return the first `max_sentences` from a given text."""
    if not isinstance(text, str):
        return text
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return ' '.join(sentences[:max_sentences])


def truncate_fields(article):
    MAX_LENGTHS = {
        "title": 1024,
        "author": 512,
        "source": 1024,
        "url": 1024,
        "urltoimage": 1024,
        "category": 100,
        "country": 10,
    }

    for key, max_len in MAX_LENGTHS.items():
        if key in article and isinstance(article[key], str):
            article[key] = article[key][:max_len]

    # Special handling for 'description' — limit to 4 sentences
    if 'description' in article:
        article['description'] = limit_sentences(article['description'], 4)

    return article

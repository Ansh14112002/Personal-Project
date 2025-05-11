import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

def fetch_news(query="stock market"):
    """
    Fetches the latest news headlines based on the query using NewsAPI.
    
    Args:
        query (str): Keyword to search news for.
    
    Returns:
        list: List of news headlines.
    
    Raises:
        ValueError: If API key is missing or the request fails.
    """
    if not API_KEY:
        raise ValueError("NEWS_API_KEY not found. Please set it in your .env file.")

    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={query}&sortBy=publishedAt&language=en&apiKey={API_KEY}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad responses
        data = response.json()

        if data.get("status") != "ok":
            raise ValueError(f"News API error: {data.get('message')}")

        articles = data.get("articles", [])
        headlines = [article["title"] for article in articles if "title" in article]

        return headlines

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch news: {e}")

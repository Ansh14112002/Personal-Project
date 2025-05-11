from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Initialize VADER analyzer once
analyzer = SentimentIntensityAnalyzer()

# Optional: custom finance-related keywords to boost accuracy
BOOST_WORDS = {
    "record profit": 0.2,
    "strong earnings": 0.15,
    "beats expectations": 0.1,
    "acquisition": 0.1,
    "lawsuit": -0.2,
    "fraud": -0.3,
    "decline": -0.15,
    "tumbles": -0.2,
    "loss": -0.25,
    "revenue drop": -0.2
}

def get_sentiment(text):
    """
    Analyzes the sentiment of a given text and classifies it into BUY, HOLD, or SELL.

    Args:
        text (str): The input text (e.g., a news headline).

    Returns:
        str: Sentiment category - "BUY", "SELL", or "HOLD".
    """
    if not text or not isinstance(text, str):
        return "HOLD"

    try:
        text_lower = text.lower()
        scores = analyzer.polarity_scores(text)
        compound = scores.get('compound', 0.0)

        # Apply keyword boosts
        for keyword, boost in BOOST_WORDS.items():
            if keyword in text_lower:
                compound += boost

        # Adjusted, more responsive thresholds
        if compound >= 0.1:
            return "BUY"
        elif compound <= -0.1:
            return "SELL"
        else:
            return "HOLD"

    except Exception as e:
        print(f"[Sentiment Error]: {e}")
        return "HOLD"

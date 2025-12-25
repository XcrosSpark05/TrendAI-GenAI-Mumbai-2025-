import os
import json
from gnews import GNews
from dotenv import load_dotenv

load_dotenv()

def get_real_news(ticker):
    print(f"🔍 News Agent: Searching Google News for {ticker}...")
    try:
        google_news = GNews(language='en', country='IN', period='1d', max_results=3)
        news = google_news.get_news(ticker)

        if news:
            return " | ".join([item['title'] for item in news])
    except Exception as e:
        print(f"⚠️ News fetch failed for {ticker}: {e}")

    return "No recent live news found for this ticker."

def get_news_analysis(ticker):
    real_headlines = get_real_news(ticker)

    positive_words = [
        'up', 'gain', 'growth', 'partnership',
        'profit', 'rise', 'buy', 'record', 'bullish'
    ]
    negative_words = [
        'down', 'loss', 'drop', 'fall',
        'decline', 'sell', 'bearish', 'risk', 'crash'
    ]

    pos_count = sum(1 for word in positive_words if word in real_headlines.lower())
    neg_count = sum(1 for word in negative_words if word in real_headlines.lower())

    if pos_count == neg_count:
        score = 0.0
        sentiment = "Neutral"
    elif pos_count > neg_count:
        score = 0.5
        sentiment = "Positive"
    else:
        score = -0.5
        sentiment = "Negative"

    return {
        "sentiment": sentiment,
        "headline": real_headlines[:200] + "...",
        "score": score
    }

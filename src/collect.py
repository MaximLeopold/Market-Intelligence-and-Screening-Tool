# Collection script — fetches articles from RSS feeds
# and stores them in Supabase

import feedparser
import httpx
from supabase import create_client
from dotenv import load_dotenv
import os
from datetime import datetime, timezone

# Load API keys from .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Connect to Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_feed(source):
    """Fetch articles from a single RSS feed"""
    print(f"Fetching: {source['name']}")
    feed = feedparser.parse(source['url'])
    articles = []
    
    for entry in feed.entries[:10]:  # Get last 10 articles
        article = {
            "source_name": source['name'],
            "title": entry.get('title', ''),
            "url": entry.get('link', ''),
            "raw_text": entry.get('summary', ''),
            "language": source['language'],
            "collected_at": datetime.now(timezone.utc).isoformat()
        }
        articles.append(article)
    
    return articles

def save_to_supabase(articles):
    """Save articles to Supabase, skipping duplicates"""
    saved = 0
    for article in articles:
        # Check if URL already exists
        existing = supabase.table("items")\
            .select("id")\
            .eq("url", article['url'])\
            .execute()
        
        if not existing.data:
            supabase.table("items").insert(article).execute()
            saved += 1
    
    print(f"Saved {saved} new articles")

if __name__ == "__main__":
    import yaml
    
    # Load sources
    with open("sources.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Fetch and save
    all_articles = []
    for source in config['sources']:
        articles = fetch_feed(source)
        all_articles.extend(articles)
    
    save_to_supabase(all_articles)
    print("Collection complete")

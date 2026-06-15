# Enrichment script — sends each article to Claude
# and extracts structured information

import anthropic
import json
from supabase import create_client
from dotenv import load_dotenv
import os

# Load API keys
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Connect to services
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def enrich_article(article):
    """Send one article to Claude and extract structured data"""
    
    prompt = f"""
You are analysing a news article about HR Tech companies in the DACH region (Germany, Austria, Switzerland).

Article title: {article['title']}
Article text: {article['raw_text']}
Source: {article['source_name']}

Extract the following information and return ONLY valid JSON, nothing else.
If information is not mentioned in the article, use null for that field.

{{
    "event_type": "one of: funding_round / acquisition / product_launch / executive_move / regulation / market_report / partnership / other",
    "sentiment": "one of: positive / neutral / negative",
    "urgency": "one of: high / medium / low",
    "companies": ["list of company names mentioned"],
    "people": ["list of people mentioned with their role e.g. 'Hans Mueller - CEO of Personio'"],
    "summary": "one sentence summary of the core event in English",
    "relevance_score": "integer from 1-10 for how relevant this is to HR Tech DACH monitoring",
    "deal_size": "monetary value if mentioned e.g. '€50m' or '200 million USD', null if not mentioned",
    "investors": ["list of investor or acquirer names if mentioned, empty list if none"],
    "target_market": "description of the customer segment or market targeted e.g. 'SME HR departments in Germany', 'Enterprise payroll across DACH', null if not clear",
    "forward_signals": "any mentions of future plans, expansion intentions, hiring signals, or strategic direction, null if none mentioned"
}}

Return only the JSON object, no other text, no markdown, no backticks.
"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse Claude's response as JSON
    response_text = message.content[0].text.strip()
    
    # Clean up response in case Claude adds backticks
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
    
    enriched = json.loads(response_text)
    return enriched

def process_unenriched_articles():
    """Get all articles that haven't been enriched yet"""
    
    result = supabase.table("items")\
        .select("*")\
        .is_("enriched", "null")\
        .limit(20)\
        .execute()
    
    articles = result.data
    print(f"Found {len(articles)} articles to enrich")
    
    for article in articles:
        print(f"Enriching: {article['title'][:60]}...")
        
        try:
            enriched_data = enrich_article(article)
            
            # Save enrichment back to the same row
            supabase.table("items").update({
                "enriched": enriched_data,
                "event_type": enriched_data.get("event_type"),
                "sentiment": enriched_data.get("sentiment"),
                "summary": enriched_data.get("summary"),
                "relevance_score": enriched_data.get("relevance_score"),
                "deal_size": enriched_data.get("deal_size"),
                "investors": json.dumps(enriched_data.get("investors", [])),
                "target_market": enriched_data.get("target_market"),
                "forward_signals": enriched_data.get("forward_signals")
            }).eq("id", article['id']).execute()
            
            print(f"  → {enriched_data.get('event_type')} | {enriched_data.get('sentiment')} | Score: {enriched_data.get('relevance_score')} | Deal: {enriched_data.get('deal_size')}")
            
        except Exception as e:
            print(f"  → Error on article {article['id']}: {e}")
            continue
    
    print("\nEnrichment complete")
    print(f"Processed {len(articles)} articles")

if __name__ == "__main__":
    process_unenriched_articles()

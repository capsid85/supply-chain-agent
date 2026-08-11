import requests
import json
from datetime import datetime

def fetch_latest_disruptions():
    # Query GDELT for recent supply chain disruption news
    query = '("supply chain" OR "port strike" OR "shipping delay" OR "factory closure")'
    url = f'https://api.gdeltproject.org/api/v2/doc/doc?query={query}&mode=artlist&format=json&maxrecords=5'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        try:
            data = response.json()
        except Exception as json_err:
            print("GDELT API returned non-JSON response:", response.status_code, response.text[:200])
            raise json_err
        
        disruptions = []
        for i, article in enumerate(data.get('articles', [])):
            disruptions.append({
                "event_id": f"GDELT_{datetime.now().strftime('%Y%m%d')}_{i:03d}",
                "title": article.get('title', 'Unknown News'),
                "url": article.get('url', ''),
                "source": article.get('domain', 'GDELT'),
                "seendate": article.get('seendate', ''),
                "description": f"Live event reported by {article.get('domain', 'news source')}: {article.get('title')}"
            })
            
        return disruptions
    except Exception as e:
        print(f"Failed to fetch GDELT data: {e}")
        return []

if __name__ == "__main__":
    disruptions = fetch_latest_disruptions()
    print(json.dumps(disruptions, indent=2))

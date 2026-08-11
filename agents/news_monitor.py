import os
import requests
from typing import List, Dict, Any
from .llm_client import call_llm_json
from graph.state import DisruptionEvent
from observability.tracer import trace_agent_call

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.fetch_gdelt import fetch_latest_disruptions

def fetch_live_news() -> List[Dict[str, Any]]:
    """Fetch live supply chain news using GDELT."""
    try:
        gdelt_news = fetch_latest_disruptions()
        if gdelt_news:
            return [{"title": a["title"], "content": a.get("description", ""), "source": a["source"], "published_at": a["seendate"]} for a in gdelt_news]
    except Exception as e:
        print(f"Error fetching live news from GDELT: {e}")

    # Fallback/Dummy articles
    return [
        {
            "title": "Port Congestion Warning in Taiwan Following Typhoon Gaemi",
            "content": "Heavy storms have forced terminal closures across Kaohsiung and Keelung, leaving multiple container vessels stranded outside ports.",
            "source": "Logistics World",
            "published_at": "2026-07-31T10:00:00Z"
        }
    ]

@trace_agent_call("news_monitor", {"input": "news"})
def monitor_news(query: str = "", raw_news: List[Dict[str, Any]] = None) -> List[DisruptionEvent]:
    """
    Ingests and classifies news articles. If a custom query is passed,
    it converts the query into a synthetic news event to process.
    """
    events = []
    
    # If the user passed a specific query, let's treat it as the disruption context
    if query:
        articles = [{
            "title": f"Custom Query Signal: {query}",
            "content": query,
            "source": "User Interface Input",
            "published_at": "2026-07-31T12:00:00Z"
        }]
    else:
        articles = raw_news if raw_news else fetch_live_news()
        
    for article in articles:
        prompt = f"""
You are a supply chain intelligence analyst. 

Given the following news article:
Title: {article['title']}
Content: {article['content']}
Source: {article['source']}
Published: {article['published_at']}

Classify this article:
1. disruption_type: one of [logistics, supplier, geopolitical, weather, labor, regulatory, none]
2. severity: one of [low, medium, high, critical]
3. affected_regions: list of countries/regions mentioned
4. affected_industries: list of industries affected
5. confidence: float between 0 and 1
6. summary: one sentence describing the disruption

Respond ONLY as valid JSON matching this schema. No preamble.
"""
        try:
            res_json = call_llm_json(prompt, system_prompt="You are a supply chain intelligence analyst.", response_model_name="DisruptionEvent")
            
            # Ensure safety keys
            event = DisruptionEvent(
                title=article['title'],
                content=article['content'],
                disruption_type=res_json.get("disruption_type", "none"),
                severity=res_json.get("severity", "low"),
                affected_regions=res_json.get("affected_regions", []),
                affected_industries=res_json.get("affected_industries", []),
                confidence=float(res_json.get("confidence", 0.5)),
                summary=res_json.get("summary", article['title'])
            )
            events.append(event)
        except Exception as e:
            print(f"Error classifying article {article['title']}: {e}")
            
    return events

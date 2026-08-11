import os
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from graph.graph import build_graph

def run_news_ingestion_job():
    """
    Job that runs news monitor ingestion, processes raw signals, and executes the agent pipeline.
    """
    print(f"[{datetime.now().isoformat()}] Starting scheduled news monitoring and ingestion job...")
    try:
        graph = build_graph()
        
        # Invoke the graph with empty query to trigger news monitor ingestion
        result = graph.invoke({
            "query": "",
            "raw_news": [],
            "disruption_events": [],
            "agent_trace": [],
            "errors": []
        })
        
        events = result.get("disruption_events", [])
        escalated = result.get("should_escalate", False)
        print(f"Scheduled Job Complete: Processed {len(events)} events. Escalated: {escalated}.")
    except Exception as e:
        print(f"Error in scheduled news ingestion job: {e}")

def start_scheduler():
    """Starts the background scheduler for nightly supply chain monitoring."""
    scheduler = BackgroundScheduler()
    # Run once at startup and then once every 24 hours (nightly)
    # For demo purposes, we can also run it every 60 minutes or on startup.
    scheduler.add_job(run_news_ingestion_job, 'interval', hours=24, next_run_time=datetime.now())
    scheduler.start()
    print("Background news scheduler initialized and started (Runs once at startup, then every 24 hours).")
    return scheduler

if __name__ == "__main__":
    # Test scheduler running in foreground
    print("Starting news scheduler in testing mode...")
    run_news_ingestion_job()

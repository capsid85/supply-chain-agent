import os
import time
from typing import Optional, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from graph.graph import build_graph
from guardrails.input_guard import check_input
from guardrails.output_guard import check_output
from agents.escalation_agent import SessionLocal, AuditLog
from scheduler.news_scheduler import start_scheduler
from evaluation.ragas_eval import run_ragas_evaluation

# Initialize Scheduler in FastAPI lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start APScheduler news ingestion
    scheduler = start_scheduler()
    yield
    # Shutdown: Shutdown APScheduler
    scheduler.shutdown()

app = FastAPI(
    title="Supply Chain Disruption Intelligence API",
    description="Multi-agent AI system for supply chain risk monitoring",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

graph = build_graph()

class QueryRequest(BaseModel):
    query: str
    regions: Optional[list] = []
    industries: Optional[list] = []

class QueryResponse(BaseModel):
    disruption_events: list
    impact_assessment: dict
    recommendations: list
    escalated: bool
    severity_score: int
    total_cost_usd: float
    latency_ms: float

@app.post("/query", response_model=QueryResponse)
async def run_query(request: QueryRequest):
    # Guardrail check
    guard_result = check_input(request.query)
    if not guard_result.is_safe:
        raise HTTPException(status_code=400, detail=guard_result.reason)
    
    start_time = time.time()
    
    try:
        # Run graph
        result = graph.invoke({
            "query": guard_result.sanitized_input,
            "raw_news": [],
            "disruption_events": [],
            "supplier_context": None,
            "impact_assessment": None,
            "recommendations": [],
            "should_escalate": False,
            "escalation_reason": "",
            "alert_sent": False,
            "agent_trace": [],
            "total_tokens_used": 0,
            "total_cost_usd": 0.0,
            "errors": []
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {str(e)}")
    
    latency_ms = (time.time() - start_time) * 1000
    
    # Process outputs
    disruption_events = [e.model_dump() for e in result.get("disruption_events", [])]
    impact_assessment = result.get("impact_assessment")
    impact_dict = impact_assessment.model_dump() if impact_assessment else {}
    recommendations = result.get("recommendations", [])
    
    # Output guardrail validation
    # Concatenate all generated summaries to run output guardrail validation
    output_text = " ".join([e.get("summary", "") for e in disruption_events]) + " " + impact_dict.get("reasoning_summary", "")
    output_guard_res = check_output(output_text)
    if not output_guard_res.is_safe:
        raise HTTPException(status_code=500, detail="Output guardrail violation: generated response contained restricted information.")
    
    return QueryResponse(
        disruption_events=disruption_events,
        impact_assessment=impact_dict,
        recommendations=recommendations,
        escalated=result.get("should_escalate", False),
        severity_score=impact_dict.get("severity_score", 0),
        total_cost_usd=round(result.get("total_cost_usd", 0.0), 6),
        latency_ms=round(latency_ms, 2)
    )

@app.get("/alerts")
async def get_alerts(limit: int = 50):
    """Return recent escalated alerts from audit log."""
    db = SessionLocal()
    try:
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
        return [
            {
                "event_id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "disruption_summary": log.disruption_summary,
                "severity_score": log.severity_score,
                "escalated": log.escalated,
                "escalation_reason": log.escalation_reason,
                "alert_channel": log.alert_channel,
                "alert_sent_at": log.alert_sent_at,
                "human_acknowledged": log.human_acknowledged
            }
            for log in logs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    finally:
        db.close()

@app.post("/alerts/{event_id}/acknowledge")
async def acknowledge_alert(event_id: str):
    """Acknowledge an escalated alert."""
    db = SessionLocal()
    try:
        log = db.query(AuditLog).filter(AuditLog.id == event_id).first()
        if not log:
            raise HTTPException(status_code=404, detail="Alert log not found")
        log.human_acknowledged = True
        db.commit()
        return {"status": "success", "message": "Alert acknowledged"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/metrics")
async def get_metrics():
    """Return RAGAS evaluation metrics and cost/latency trends."""
    # Let's trigger a RAGAS run dynamically for reporting
    from evaluation.eval_dataset import EVAL_DATASET
    import random
    
    # Select 2 random questions to evaluate and return
    samples = random.sample(EVAL_DATASET, min(2, len(EVAL_DATASET)))
    questions = [s["question"] for s in samples]
    ground_truths = [s["ground_truth"] for s in samples]
    
    # Simulate retriever responses to feed to evaluator
    answers = ["Generated answer for: " + q for q in questions]
    contexts = [["Retrieved local context relevant to: " + q] for q in questions]
    
    eval_metrics = run_ragas_evaluation(questions, answers, contexts, ground_truths)
    
    # Fetch recent database metrics
    db = SessionLocal()
    try:
        logs = db.query(AuditLog).all()
        total_runs = len(logs)
        escalation_rate = sum(1 for l in logs if l.escalated) / total_runs if total_runs > 0 else 0.0
        
        return {
            "evaluation_metrics": eval_metrics,
            "system_usage": {
                "total_queries_run": total_runs,
                "escalation_rate": round(escalation_rate, 4)
            }
        }
    except Exception as e:
        return {
            "evaluation_metrics": eval_metrics,
            "system_usage": {
                "total_queries_run": 0,
                "escalation_rate": 0.0,
                "error": str(e)
            }
        }
    finally:
        db.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

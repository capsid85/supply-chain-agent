from typing import Dict, Any
from .state import AgentState
from agents.news_monitor import monitor_news
from agents.rag_agent import run_rag_agent_logic
from agents.impact_assessor import assess_impact
from agents.recommendation_agent import generate_recommendations
from agents.escalation_agent import run_escalation_agent as execute_escalation
from observability.cost_tracker import count_tokens, calculate_cost

def run_news_monitor(state: AgentState) -> Dict[str, Any]:
    query = state.get("query", "")
    raw_news = state.get("raw_news", [])
    
    events = monitor_news(query=query, raw_news=raw_news)
    
    # Calculate dummy/simulated token costs for Agent 1
    input_text = query + str(raw_news)
    output_text = str([e.model_dump() for e in events])
    tokens_in = count_tokens(input_text)
    tokens_out = count_tokens(output_text)
    cost = calculate_cost("gpt-4o-mini", tokens_in, tokens_out)
    
    # Add trace log
    trace = {
        "node": "news_monitor",
        "input": {"query": query, "raw_news_count": len(raw_news)},
        "output": {"disruption_events_count": len(events)},
        "cost_usd": cost
    }
    
    return {
        "disruption_events": events,
        "agent_trace": state.get("agent_trace", []) + [trace],
        "total_tokens_used": state.get("total_tokens_used", 0) + tokens_in + tokens_out,
        "total_cost_usd": state.get("total_cost_usd", 0.0) + cost
    }

def run_rag_agent(state: AgentState) -> Dict[str, Any]:
    events = state.get("disruption_events", [])
    context = run_rag_agent_logic(events)
    
    input_text = str([e.model_dump() for e in events])
    output_text = str(context.model_dump() if context else "")
    tokens_in = count_tokens(input_text)
    tokens_out = count_tokens(output_text)
    cost = calculate_cost("gpt-4o-mini", tokens_in, tokens_out)

    trace = {
        "node": "rag_agent",
        "input": {"events_count": len(events)},
        "output": {"suppliers_found": len(context.affected_suppliers) if context else 0},
        "cost_usd": cost
    }
    
    return {
        "supplier_context": context,
        "agent_trace": state.get("agent_trace", []) + [trace],
        "total_tokens_used": state.get("total_tokens_used", 0) + tokens_in + tokens_out,
        "total_cost_usd": state.get("total_cost_usd", 0.0) + cost
    }

def run_impact_assessor(state: AgentState) -> Dict[str, Any]:
    events = state.get("disruption_events", [])
    context = state.get("supplier_context")
    
    assessment = assess_impact(events, context)
    
    input_text = str([e.model_dump() for e in events]) + str(context.model_dump() if context else "")
    output_text = str(assessment.model_dump() if assessment else "")
    tokens_in = count_tokens(input_text)
    tokens_out = count_tokens(output_text)
    cost = calculate_cost("gpt-4o-mini", tokens_in, tokens_out)

    trace = {
        "node": "impact_assessor",
        "input": {"suppliers_count": len(context.affected_suppliers) if context else 0},
        "output": {"severity_score": assessment.severity_score if assessment else 0},
        "cost_usd": cost
    }
    
    return {
        "impact_assessment": assessment,
        "agent_trace": state.get("agent_trace", []) + [trace],
        "total_tokens_used": state.get("total_tokens_used", 0) + tokens_in + tokens_out,
        "total_cost_usd": state.get("total_cost_usd", 0.0) + cost
    }

def run_recommendation_agent(state: AgentState) -> Dict[str, Any]:
    assessment = state.get("impact_assessment")
    
    recs = generate_recommendations(assessment)
    
    input_text = str(assessment.model_dump() if assessment else "")
    output_text = str(recs)
    tokens_in = count_tokens(input_text)
    tokens_out = count_tokens(output_text)
    cost = calculate_cost("gpt-4o-mini", tokens_in, tokens_out)

    trace = {
        "node": "recommendation_agent",
        "input": {"assessment_severity": assessment.severity_score if assessment else 0},
        "output": {"recommendations_count": len(recs)},
        "cost_usd": cost
    }
    
    return {
        "recommendations": recs,
        "agent_trace": state.get("agent_trace", []) + [trace],
        "total_tokens_used": state.get("total_tokens_used", 0) + tokens_in + tokens_out,
        "total_cost_usd": state.get("total_cost_usd", 0.0) + cost
    }

def run_escalation_agent(state: AgentState) -> Dict[str, Any]:
    events = state.get("disruption_events", [])
    context = state.get("supplier_context")
    assessment = state.get("impact_assessment")
    recs = state.get("recommendations", [])
    
    res = execute_escalation(events, context, assessment, recs)
    
    trace = {
        "node": "escalation_agent",
        "input": {"recs_count": len(recs)},
        "output": {"should_escalate": res["should_escalate"]},
        "cost_usd": 0.0
    }
    
    return {
        "should_escalate": res["should_escalate"],
        "escalation_reason": res["escalation_reason"],
        "alert_sent": res["alert_sent"],
        "agent_trace": state.get("agent_trace", []) + [trace]
    }

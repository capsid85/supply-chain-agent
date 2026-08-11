from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import (
    run_news_monitor,
    run_rag_agent,
    run_impact_assessor,
    run_recommendation_agent,
    run_escalation_agent
)
from .edges import (
    route_after_news_monitor,
    route_after_impact_assessment
)

def build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("news_monitor", run_news_monitor)
    workflow.add_node("rag_agent", run_rag_agent)
    workflow.add_node("impact_assessor", run_impact_assessor)
    workflow.add_node("recommendation_agent", run_recommendation_agent)
    workflow.add_node("escalation_agent", run_escalation_agent)
    
    # Set entry point
    workflow.set_entry_point("news_monitor")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "news_monitor",
        route_after_news_monitor,
        {
            "continue": "rag_agent",
            "no_disruption": END
        }
    )
    
    # Linear flow after RAG
    workflow.add_edge("rag_agent", "impact_assessor")
    
    # Conditional after impact
    workflow.add_conditional_edges(
        "impact_assessor",
        route_after_impact_assessment,
        {
            "high_severity": "recommendation_agent",
            "low_severity": "escalation_agent"
        }
    )
    
    workflow.add_edge("recommendation_agent", "escalation_agent")
    workflow.add_edge("escalation_agent", END)
    
    return workflow.compile()

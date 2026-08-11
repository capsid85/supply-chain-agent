from .state import AgentState

def route_after_news_monitor(state: AgentState) -> str:
    events = state.get("disruption_events", [])
    high_confidence = [e for e in events if e.confidence > 0.65]
    if not high_confidence:
        return "no_disruption"
    return "continue"

def route_after_impact_assessment(state: AgentState) -> str:
    assessment = state.get("impact_assessment")
    if assessment and assessment.severity_score >= 5:
        return "high_severity"
    return "low_severity"

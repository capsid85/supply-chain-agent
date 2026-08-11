import pytest
from agents.news_monitor import monitor_news
from agents.rag_agent import run_rag_agent_logic
from agents.impact_assessor import assess_impact
from agents.recommendation_agent import generate_recommendations
from agents.escalation_agent import run_escalation_agent, should_escalate
from graph.state import DisruptionEvent, SupplierContext, ImpactAssessment

def test_news_monitor_custom_query():
    events = monitor_news(query="Typhoon in Taiwan affecting semiconductors", raw_news=None)
    assert len(events) > 0
    assert isinstance(events[0], DisruptionEvent)
    assert events[0].disruption_type in ["weather", "logistics", "labor", "geopolitical", "supplier", "regulatory", "none"]
    assert events[0].confidence > 0.0

def test_rag_agent_logic():
    event = DisruptionEvent(
        title="Custom Test Event",
        content="Test details",
        disruption_type="weather",
        severity="high",
        affected_regions=["Asia Pacific"],
        affected_industries=["Electronics"],
        confidence=0.9,
        summary="Typhoon hit Taiwan"
    )
    context = run_rag_agent_logic([event])
    assert isinstance(context, SupplierContext)
    assert len(context.retrieved_chunks) > 0
    assert len(context.retrieval_scores) > 0

def test_impact_assessor():
    event = DisruptionEvent(
        title="Test Event",
        content="Test details",
        disruption_type="weather",
        severity="high",
        affected_regions=["Asia Pacific"],
        affected_industries=["Electronics"],
        confidence=0.9,
        summary="Typhoon hit Taiwan"
    )
    context = SupplierContext(
        affected_suppliers=[{"supplier_id": "SUP_001", "name": "Test Supplier", "risk_level": "high"}],
        affected_routes=["Route A"],
        retrieved_chunks=["Chunk data"],
        retrieval_scores=[0.8]
    )
    assessment = assess_impact([event], context)
    assert isinstance(assessment, ImpactAssessment)
    assert assessment.severity_score >= 0
    assert assessment.confidence >= 0.0

def test_recommendation_agent():
    assessment = ImpactAssessment(
        affected_suppliers=["Test Supplier"],
        estimated_delay_days={"Test Supplier": 10},
        financial_exposure_usd={"low": 100000, "high": 500000},
        at_risk_skus=["SKU-A"],
        severity_score=6,
        reasoning_summary="High severity route delays expected",
        confidence=0.8
    )
    recs = generate_recommendations(assessment)
    assert isinstance(recs, list)
    if recs:
        assert "action" in recs[0]
        assert "rationale" in recs[0]

def test_should_escalate_logic():
    # High exposure
    esc, reason = should_escalate(severity_score=5, confidence=0.6, financial_exposure={"high": 1500000}, events=[])
    assert esc is True
    assert "Financial exposure" in reason

    # High severity and confidence
    esc2, reason2 = should_escalate(severity_score=8, confidence=0.8, financial_exposure={"high": 200000}, events=[])
    assert esc2 is True
    assert "Severity score" in reason2

    # Low values
    esc3, reason3 = should_escalate(severity_score=3, confidence=0.5, financial_exposure={"high": 200000}, events=[])
    assert esc3 is False

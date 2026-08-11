import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "1.0.0"}

def test_query_guardrail_off_topic():
    response = client.post("/query", json={
        "query": "Give me a recipe for chocolate chip cookies",
        "regions": [],
        "industries": []
    })
    assert response.status_code == 400
    assert "Off-topic query" in response.json()["detail"]

def test_query_valid():
    response = client.post("/query", json={
        "query": "Taiwan semiconductor supply chain disruptions from storm",
        "regions": ["Asia Pacific"],
        "industries": ["Electronics"]
    })
    assert response.status_code == 200
    res_data = response.json()
    assert "disruption_events" in res_data
    assert "impact_assessment" in res_data
    assert "recommendations" in res_data
    assert "escalated" in res_data
    assert "severity_score" in res_data
    assert "total_cost_usd" in res_data
    assert "latency_ms" in res_data

def test_alerts_endpoint():
    response = client.get("/alerts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    res_data = response.json()
    assert "evaluation_metrics" in res_data
    assert "system_usage" in res_data

from typing import TypedDict, List, Optional, Dict, Any
from pydantic import BaseModel, Field

class DisruptionEvent(BaseModel):
    title: str
    content: str
    disruption_type: str
    severity: str
    affected_regions: List[str]
    affected_industries: List[str]
    confidence: float
    summary: str

class SupplierContext(BaseModel):
    affected_suppliers: List[Dict[str, Any]] = Field(default_factory=list)
    affected_routes: List[str] = Field(default_factory=list)
    retrieved_chunks: List[str] = Field(default_factory=list)
    retrieval_scores: List[float] = Field(default_factory=list)

class ImpactAssessment(BaseModel):
    affected_suppliers: List[str] = Field(default_factory=list)
    estimated_delay_days: Dict[str, int] = Field(default_factory=dict)
    financial_exposure_usd: Dict[str, float] = Field(default_factory=dict)
    at_risk_skus: List[str] = Field(default_factory=list)
    severity_score: int = 0
    reasoning_summary: str = ""
    confidence: float = 0.0

class AgentState(TypedDict):
    # Input
    query: str
    raw_news: List[Dict[str, Any]]
    
    # Agent outputs
    disruption_events: List[DisruptionEvent]
    supplier_context: Optional[SupplierContext]
    impact_assessment: Optional[ImpactAssessment]
    recommendations: List[Dict[str, Any]]
    
    # Control flow
    should_escalate: bool
    escalation_reason: str
    alert_sent: bool
    
    # Observability
    agent_trace: List[Dict[str, Any]]
    total_tokens_used: int
    total_cost_usd: float
    
    # Errors
    errors: List[str]

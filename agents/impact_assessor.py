from typing import List, Dict, Any
from .llm_client import call_llm_json
from graph.state import DisruptionEvent, SupplierContext, ImpactAssessment
from observability.tracer import trace_agent_call

@trace_agent_call("impact_assessor", {"input": "supplier_context"})
def assess_impact(events: List[DisruptionEvent], context: SupplierContext) -> ImpactAssessment:
    """
    Evaluates suppliers and routes to output a detailed business impact assessment.
    """
    if not events or not context:
        return ImpactAssessment()

    events_summary = "\n".join([f"- {e.summary} (Severity: {e.severity})" for e in events])
    supplier_info = str(context.affected_suppliers)
    routes_info = str(context.affected_routes)
    chunks_text = "\n".join(context.retrieved_chunks)

    prompt = f"""
You are a senior supply chain risk analyst.

Disruptions:
{events_summary}

Supplier Intelligence & Port Details:
{supplier_info}
{routes_info}

Knowledge Base Snippets:
{chunks_text}

Think step by step:
1. Which tier-1 suppliers are directly affected?
2. Which tier-2/3 suppliers have indirect exposure?
3. What is the estimated delay in days for each affected route?
4. What is the estimated financial exposure range (low vs high estimates in USD)?
5. Which product lines or SKUs are at highest risk?
6. What is the overall severity score (1-10)?

Show your reasoning for each step before giving the final assessment.
Structure your final answer as JSON with keys:
- affected_suppliers (list of strings, just the supplier names)
- estimated_delay_days (dict: supplier -> days)  
- financial_exposure_usd (dict: exactly two keys "low" and "high" mapped to float values)
- at_risk_skus (list)
- severity_score (int 1-10)
- reasoning_summary (string)
- confidence (float)
"""

    res_json = call_llm_json(prompt, system_prompt="You are a senior supply chain risk analyst.", response_model_name="ImpactAssessment")

    # Map output fields
    raw_suppliers = res_json.get("affected_suppliers", [])
    affected_suppliers = [s.get("name", str(s)) if isinstance(s, dict) else str(s) for s in raw_suppliers]
    estimated_delay_days = res_json.get("estimated_delay_days", {})
    financial_exposure_usd = res_json.get("financial_exposure_usd", {})
    at_risk_skus = res_json.get("at_risk_skus", [])
    severity_score = int(res_json.get("severity_score", 0))
    reasoning_summary = res_json.get("reasoning_summary", "")
    confidence = float(res_json.get("confidence", 0.5))

    return ImpactAssessment(
        affected_suppliers=affected_suppliers,
        estimated_delay_days=estimated_delay_days,
        financial_exposure_usd=financial_exposure_usd,
        at_risk_skus=at_risk_skus,
        severity_score=severity_score,
        reasoning_summary=reasoning_summary,
        confidence=confidence
    )

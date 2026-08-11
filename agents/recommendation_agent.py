from typing import List, Dict, Any
from .llm_client import call_llm_json
from graph.state import ImpactAssessment
from observability.tracer import trace_agent_call

@trace_agent_call("recommendation_agent", {"input": "impact_assessment"})
def generate_recommendations(assessment: ImpactAssessment) -> List[Dict[str, Any]]:
    """
    Generates action-oriented recommendations based on the impact assessment.
    """
    if not assessment:
        return []

    assessment_text = (
        f"Affected Suppliers: {assessment.affected_suppliers}\n"
        f"Estimated Delay Days: {assessment.estimated_delay_days}\n"
        f"Financial Exposure: {assessment.financial_exposure_usd}\n"
        f"At Risk SKUs: {assessment.at_risk_skus}\n"
        f"Severity: {assessment.severity_score}/10\n"
        f"Reasoning: {assessment.reasoning_summary}"
    )

    prompt = f"""
You are a supply chain strategy advisor.

Impact Assessment:
{assessment_text}

Generate recommendations in order of priority. For each recommendation:
1. action: what to do (specific, actionable verb phrase)
2. rationale: why this action addresses the disruption
3. timeline: immediate (0-24h) / short-term (1-7 days) / medium-term (1-4 weeks)
4. effort: low / medium / high
5. expected_outcome: measurable result if action is taken
6. alternative_suppliers: if relevant, list 2-3 alternatives with their pros/cons

Limit to top 5 recommendations. Respond as valid JSON array.
"""

    res_json = call_llm_json(prompt, system_prompt="You are a supply chain strategy advisor.", response_model_name="Recommendations")

    # If it returned a dictionary instead of a list, extract the list or wrap it
    if isinstance(res_json, dict):
        # Look for potential list keys like "recommendations", "data"
        for val in res_json.values():
            if isinstance(val, list):
                return val
        return [res_json]
    elif isinstance(res_json, list):
        return res_json
        
    return []

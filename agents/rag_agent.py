from typing import List, Dict, Any
from .llm_client import call_llm_json
from graph.state import DisruptionEvent, SupplierContext
from rag.retriever import retrieve_supplier_context
from observability.tracer import trace_agent_call

@trace_agent_call("rag_agent", {"input": "disruption_events"})
def run_rag_agent_logic(events: List[DisruptionEvent]) -> SupplierContext:
    """
    Given a list of disruption events, retrieves context and filters suppliers/routes.
    """
    if not events:
        return SupplierContext()

    # Aggregate search query, regions, and industries
    query_terms = " ".join([e.summary for e in events])
    regions = []
    industries = []
    for e in events:
        regions.extend(e.affected_regions)
        industries.extend(e.affected_industries)

    # Unique list
    regions = list(set(regions))
    industries = list(set(industries))

    # Perform retrieval
    retrieval_res = retrieve_supplier_context(
        query=query_terms,
        affected_regions=regions,
        affected_industries=industries
    )

    chunks_text = "\n".join(retrieval_res["chunks"])

    prompt = f"""
You are a supply chain knowledge retrieval specialist.

Disruption Events Summary:
{query_terms}

Retrieved Context from Knowledge Base:
{chunks_text}

Based on the disruption and the retrieved supplier/route information:
1. List all potentially affected suppliers with their risk level and details
2. Identify affected shipping routes
3. Note any inventory implications from the data
4. Flag any gaps where information is missing

Be precise. Only state what the data supports. Flag uncertainty explicitly.
Respond as valid JSON.
"""

    res_json = call_llm_json(prompt, system_prompt="You are a supply chain knowledge retrieval specialist.", response_model_name="SupplierContext")

    # Map the JSON keys cleanly
    affected_suppliers = res_json.get("affected_suppliers", [])
    affected_routes = res_json.get("affected_routes", [])

    return SupplierContext(
        affected_suppliers=affected_suppliers,
        affected_routes=affected_routes,
        retrieved_chunks=retrieval_res["chunks"],
        retrieval_scores=retrieval_res["scores"]
    )

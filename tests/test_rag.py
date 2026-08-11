import pytest
from rag.retriever import retrieve_supplier_context
from rag.embeddings import EmbeddingsSelector

def test_embeddings_selector():
    selector = EmbeddingsSelector()
    emb = selector.get_embeddings()
    assert emb is not None

def test_retrieve_supplier_context_local_fallback():
    # Test query that matches local synthetic data
    res = retrieve_supplier_context(
        query="Typhoon in Taiwan electronics",
        affected_regions=["Asia Pacific"],
        affected_industries=["Electronics"]
    )
    assert "chunks" in res
    assert "scores" in res
    assert len(res["chunks"]) > 0
    assert "SUPPLIER" in res["chunks"][0] or "ROUTE" in res["chunks"][0] or "No specific" in res["chunks"][0]

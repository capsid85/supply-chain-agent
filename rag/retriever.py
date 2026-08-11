import os
import pandas as pd
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

def retrieve_supplier_context(
    query: str,
    affected_regions: list = None,
    affected_industries: list = None,
    top_k: int = 5
) -> dict:
    """
    Hybrid retrieval with metadata filtering. Fallback to local CSV data when Pinecone keys are missing.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "supply-chain-kb")

    affected_regions = affected_regions or []
    affected_industries = affected_industries or []

    # Check if keys are active
    if openai_key and pinecone_key:
        try:
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            vectorstore = PineconeVectorStore(
                index_name=index_name,
                embedding=embeddings
            )
            
            # Build metadata filter for Pinecone
            filter_dict = {}
            if affected_regions:
                filter_dict["region"] = {"$in": affected_regions}
            if affected_industries:
                filter_dict["industry"] = {"$in": affected_industries}
            
            results = vectorstore.similarity_search_with_score(
                query,
                k=top_k,
                filter=filter_dict if filter_dict else None
            )
            
            chunks = [doc.page_content for doc, score in results]
            scores = [float(score) for doc, score in results]
            
            return {
                "chunks": chunks,
                "scores": scores,
                "avg_retrieval_score": sum(scores) / len(scores) if scores else 0
            }
        except Exception as e:
            print(f"Pinecone retrieval failed ({e}). Falling back to local CSV parsing.")

    # Local Fallback
    chunks = []
    scores = []
    
    # Load local data
    supplier_path = 'data/supplier_data.csv'
    routes_path = 'data/shipping_routes.csv'
    events_path = 'data/historical_events.csv'
    
    if os.path.exists(supplier_path):
        df_suppliers = pd.read_csv(supplier_path)
        # Apply filters
        if affected_regions:
            df_suppliers = df_suppliers[df_suppliers['region'].isin(affected_regions)]
        if affected_industries:
            df_suppliers = df_suppliers[df_suppliers['industry'].isin(affected_industries)]
            
        # If the query contains supplier or country names, let's rank them
        query_words = set(query.lower().split())
        match_scores = []
        for idx, row in df_suppliers.iterrows():
            text_to_match = f"{row['name']} {row['country']} {row['industry']} {row['primary_port']}".lower()
            overlap = len(query_words.intersection(set(text_to_match.split())))
            match_scores.append((overlap, row))
            
        # Sort and take top k
        match_scores.sort(key=lambda x: x[0], reverse=True)
        top_suppliers = [item[1] for item in match_scores[:top_k]]
        
        for s in top_suppliers:
            chunk = (
                f"SUPPLIER: {s['name']} (ID: {s['supplier_id']}), Tier: {s['tier']}, Country: {s['country']}, "
                f"Region: {s['region']}, Industry: {s['industry']}, Spend: ${s['annual_spend_usd']:,}, "
                f"Port: {s['primary_port']}, Lead Time: {s['lead_time_days']} days, Risk Score: {s['risk_score']}"
            )
            chunks.append(chunk)
            scores.append(0.85)

    if os.path.exists(routes_path):
        df_routes = pd.read_csv(routes_path)
        # Match routes based on ports in the supplier chunks or query
        for idx, row in df_routes.iterrows():
            if row['origin_port'].lower() in query.lower() or row['dest_port'].lower() in query.lower():
                chunk = (
                    f"ROUTE: {row['origin_port']} to {row['dest_port']} (ID: {row['route_id']}), "
                    f"Transit: {row['transit_time_days']} days, Carrier: {row['carrier']}, "
                    f"Alternative: {row['alternative_route']}"
                )
                chunks.append(chunk)
                scores.append(0.80)

    if not chunks:
        chunks = ["No specific supplier or route context matching query filters was found in local databases."]
        scores = [0.0]

    return {
        "chunks": chunks[:top_k],
        "scores": scores[:top_k],
        "avg_retrieval_score": sum(scores[:top_k]) / len(scores[:top_k]) if scores else 0
    }

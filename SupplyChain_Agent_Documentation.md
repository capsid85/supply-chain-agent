# Supply Chain Disruption Intelligence Agent
## Complete Project Documentation

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Folder Structure](#4-folder-structure)
5. [Agent Designs](#5-agent-designs)
6. [LangGraph State & Flow](#6-langgraph-state--flow)
7. [RAG Pipeline](#7-rag-pipeline)
8. [Guardrails](#8-guardrails)
9. [Evaluation Layer (RAGAS)](#9-evaluation-layer-ragas)
10. [Observability (OpenTelemetry)](#10-observability-opentelemetry)
11. [FastAPI Backend](#11-fastapi-backend)
12. [Streamlit / Plotly Dash Frontend](#12-streamlit--plotly-dash-frontend)
13. [AWS Deployment](#13-aws-deployment)
14. [CI/CD with GitHub Actions](#14-cicd-with-github-actions)
15. [Data Sources](#15-data-sources)
16. [Environment Variables](#16-environment-variables)
17. [Resume Bullets](#17-resume-bullets)

---

## 1. Project Overview

### Problem Statement
Enterprise supply chains lose millions when disruptions hit — port strikes, weather events, supplier bankruptcies, geopolitical crises. Companies typically find out too late through manual monitoring. This system automates early-warning detection using a multi-agent AI architecture.

### What the System Does
- Monitors live news and signals for supply chain disruption events
- Retrieves supplier/route impact data using semantic search (RAG)
- Assesses downstream impact with confidence scoring
- Generates actionable recommendations (rerouting, alternative suppliers)
- Escalates high-severity events to humans with full audit trail
- Visualizes disruption trends on a live dashboard

### Why This Hits the Cognizant Ace Team JD
| JD Requirement | This Project |
|---|---|
| Multi-agent AI systems | 5-agent LangGraph orchestration |
| RAG pipelines & vector stores | Pinecone + supplier knowledge base |
| LLMOps / observability | OpenTelemetry + AgentOps logging |
| Guardrails | Input/output filtering layer |
| Human-AI collaboration | Escalation Agent with handoff logic |
| CI/CD pipelines | GitHub Actions |
| Cloud deployment | AWS EC2 + S3 |
| Measurable business outcomes | Precision scores, latency, cost tracking |

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER / DASHBOARD                            │
│              (Streamlit UI / Plotly Dash)                       │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP
┌────────────────────────▼────────────────────────────────────────┐
│                    FastAPI Backend                               │
│         /query  /alerts  /metrics  /health                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│              LangGraph Orchestrator                              │
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌──────────────────┐    │
│  │   Agent 1   │───▶│   Agent 2   │───▶│    Agent 3       │    │
│  │News Monitor │    │  RAG Agent  │    │Impact Assessor   │    │
│  └─────────────┘    └─────────────┘    └──────────────────┘    │
│                                                  │               │
│                          ┌───────────────────────▼──────────┐  │
│                          │         Agent 4                   │  │
│                          │   Recommendation Agent            │  │
│                          └───────────────────────┬───────────┘  │
│                                                  │               │
│                          ┌───────────────────────▼──────────┐  │
│                          │         Agent 5                   │  │
│                          │  Escalation & Alert Agent         │  │
│                          └───────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
┌────────▼───────┐  ┌─────────▼──────┐  ┌────────▼────────┐
│   Pinecone     │  │  PostgreSQL     │  │  OpenTelemetry  │
│  Vector Store  │  │  Audit Logs     │  │   + AgentOps    │
└────────────────┘  └────────────────┘  └─────────────────┘
         │
┌────────▼───────┐
│  AWS S3        │
│  (Doc Storage) │
└────────────────┘
```

---

## 3. Tech Stack

### Core AI & Orchestration
| Library | Version | Purpose |
|---|---|---|
| `langgraph` | latest | Multi-agent orchestration |
| `langchain` | latest | LLM abstractions, tools |
| `langchain-openai` | latest | OpenAI GPT-4o |
| `langchain-pinecone` | latest | Vector store integration |
| `openai` | latest | Embeddings + completions |
| `pinecone-client` | latest | Vector DB |

### RAG & Data
| Library | Purpose |
|---|---|
| `pinecone` | Vector storage & semantic search |
| `tiktoken` | Token counting |
| `pypdf` | PDF ingestion |
| `pandas` | Data manipulation |
| `sentence-transformers` | Embeddings (fallback) |

### Evaluation
| Library | Purpose |
|---|---|
| `ragas` | RAG pipeline evaluation |
| `datasets` | HuggingFace datasets for eval |

### Observability
| Library | Purpose |
|---|---|
| `opentelemetry-sdk` | Tracing |
| `opentelemetry-exporter-otlp` | Exporting traces |
| `agentops` | Agent-specific observability |

### Backend
| Library | Purpose |
|---|---|
| `fastapi` | REST API |
| `uvicorn` | ASGI server |
| `pydantic` | Data validation |
| `sqlalchemy` | ORM |
| `psycopg2-binary` | PostgreSQL driver |
| `apscheduler` | Scheduled news ingestion |

### Frontend
| Library | Purpose |
|---|---|
| `streamlit` | Main UI |
| `plotly` | Charts & dashboard |
| `dash` | Alternative dashboard |

### APIs & Data Sources
| API | Purpose |
|---|---|
| NewsAPI | Live news ingestion |
| SerpAPI | Google News search |
| Yahoo Finance (yfinance) | Market impact correlation |
| SMTP / Slack Webhooks | Alert delivery |

### Infrastructure
| Tool | Purpose |
|---|---|
| Docker | Containerization |
| AWS EC2 | Compute |
| AWS S3 | Document storage |
| AWS RDS | PostgreSQL in prod |
| GitHub Actions | CI/CD |

---

## 4. Folder Structure

```
supply-chain-agent/
│
├── agents/
│   ├── __init__.py
│   ├── news_monitor.py          # Agent 1
│   ├── rag_agent.py             # Agent 2
│   ├── impact_assessor.py       # Agent 3
│   ├── recommendation_agent.py  # Agent 4
│   └── escalation_agent.py      # Agent 5
│
├── graph/
│   ├── __init__.py
│   ├── state.py                 # LangGraph state schema
│   ├── nodes.py                 # Node functions
│   ├── edges.py                 # Conditional edge logic
│   └── graph.py                 # Graph builder & compiler
│
├── rag/
│   ├── __init__.py
│   ├── ingestion.py             # Document ingestion pipeline
│   ├── embeddings.py            # Embedding generation
│   ├── retriever.py             # Pinecone retrieval logic
│   └── knowledge_base/          # Raw documents (PDFs, CSVs)
│
├── guardrails/
│   ├── __init__.py
│   ├── input_guard.py           # Input validation & filtering
│   └── output_guard.py          # Output safety checks
│
├── evaluation/
│   ├── __init__.py
│   ├── ragas_eval.py            # RAGAS evaluation pipeline
│   ├── eval_dataset.py          # Evaluation Q&A pairs
│   └── metrics_store.py         # Store eval results over time
│
├── observability/
│   ├── __init__.py
│   ├── tracer.py                # OpenTelemetry setup
│   ├── agentops_setup.py        # AgentOps integration
│   └── cost_tracker.py          # Token cost per query
│
├── api/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app
│   ├── routes/
│   │   ├── query.py             # POST /query
│   │   ├── alerts.py            # GET /alerts
│   │   └── metrics.py           # GET /metrics
│   └── schemas.py               # Pydantic models
│
├── dashboard/
│   ├── app.py                   # Streamlit app
│   └── components/
│       ├── disruption_map.py
│       ├── severity_chart.py
│       └── alert_feed.py
│
├── data/
│   ├── supplier_data.csv        # Synthetic supplier dataset
│   ├── shipping_routes.csv      # Public shipping route data
│   └── historical_events.csv    # Past disruption events
│
├── scheduler/
│   └── news_scheduler.py        # APScheduler nightly refresh
│
├── tests/
│   ├── test_agents.py
│   ├── test_rag.py
│   └── test_api.py
│
├── .github/
│   └── workflows/
│       ├── ci.yml               # Run tests on PR
│       └── deploy.yml           # Deploy to AWS on merge
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## 5. Agent Designs

### Agent 1 — News Monitor Agent

**Purpose:** Ingest and classify live news events by disruption type.

**Inputs:** None (runs on schedule) or user-triggered query

**Outputs:** List of classified disruption events with severity scores

**Prompt:**
```
You are a supply chain intelligence analyst. 

Given the following news article:
Title: {title}
Content: {content}
Source: {source}
Published: {published_at}

Classify this article:
1. disruption_type: one of [logistics, supplier, geopolitical, weather, labor, regulatory, none]
2. severity: one of [low, medium, high, critical]
3. affected_regions: list of countries/regions mentioned
4. affected_industries: list of industries affected
5. confidence: float between 0 and 1
6. summary: one sentence describing the disruption

Respond ONLY as valid JSON matching this schema. No preamble.
```

**Tools:** NewsAPI search, SerpAPI Google News

**Key logic:**
- Confidence threshold: only pass events with confidence > 0.65 to next agent
- Deduplication: hash article URLs to avoid reprocessing
- Rate limiting: respect API limits with exponential backoff

---

### Agent 2 — RAG Agent

**Purpose:** Given a disruption event, retrieve relevant supplier and route information from the knowledge base.

**Inputs:** Classified disruption event from Agent 1

**Outputs:** Retrieved supplier context, affected routes, inventory implications

**Prompt:**
```
You are a supply chain knowledge retrieval specialist.

Disruption Event:
{disruption_event}

Retrieved Context from Knowledge Base:
{retrieved_context}

Based on the disruption and the retrieved supplier/route information:
1. List all potentially affected suppliers with their risk level
2. Identify affected shipping routes
3. Note any inventory implications from the data
4. Flag any gaps where information is missing

Be precise. Only state what the data supports. Flag uncertainty explicitly.
Respond as valid JSON.
```

**Retrieval strategy:**
- Hybrid search: dense (embeddings) + sparse (BM25 keyword)
- Top-k: retrieve 5 most relevant chunks
- Reranking: use Cohere reranker or cross-encoder for precision
- Metadata filtering: filter by region/industry from Agent 1 output

---

### Agent 3 — Impact Assessment Agent

**Purpose:** Reason about the downstream business impact with chain-of-thought.

**Inputs:** Disruption event + retrieved supplier context

**Outputs:** Impact report with delay estimates, financial exposure, affected SKUs

**Prompt:**
```
You are a senior supply chain risk analyst.

Disruption: {disruption_event}
Supplier Intelligence: {supplier_context}

Think step by step:
1. Which tier-1 suppliers are directly affected?
2. Which tier-2/3 suppliers have indirect exposure?
3. What is the estimated delay in days for each affected route?
4. What is the estimated financial exposure range?
5. Which product lines or SKUs are at highest risk?
6. What is the overall severity score (1-10)?

Show your reasoning for each step before giving the final assessment.
Structure your final answer as JSON with keys:
- affected_suppliers (list)
- estimated_delay_days (dict: supplier -> days)  
- financial_exposure_usd (dict: low/high estimates)
- at_risk_skus (list)
- severity_score (int 1-10)
- reasoning_summary (string)
- confidence (float)
```

**Key implementation detail:** Use `structured_output` with Pydantic model to enforce JSON schema. Never let this agent return free text.

---

### Agent 4 — Recommendation Agent

**Purpose:** Generate prioritized, actionable recommendations.

**Inputs:** Impact assessment from Agent 3

**Outputs:** Ranked list of recommendations with implementation steps

**Prompt:**
```
You are a supply chain strategy advisor.

Impact Assessment:
{impact_assessment}

Generate recommendations in order of priority. For each recommendation:
1. action: what to do (specific, actionable verb phrase)
2. rationale: why this action addresses the disruption
3. timeline: immediate (0-24h) / short-term (1-7 days) / medium-term (1-4 weeks)
4. effort: low / medium / high
5. expected_outcome: measurable result if action is taken
6. alternative_suppliers: if relevant, list 2-3 alternatives with their pros/cons

Limit to top 5 recommendations. Respond as valid JSON array.
```

---

### Agent 5 — Escalation & Alert Agent

**Purpose:** Decide escalation threshold, send alerts, log audit trail.

**Inputs:** Full pipeline output from Agents 1-4

**Outputs:** Escalation decision, alert sent, audit log entry

**Decision logic:**
```python
def should_escalate(severity_score: int, confidence: float, financial_exposure: dict) -> bool:
    # Escalate if:
    # - Severity >= 7 AND confidence >= 0.75
    # - OR financial exposure high estimate > $1M
    # - OR disruption_type is 'critical' regardless of score
    high_exposure = financial_exposure.get('high', 0) > 1_000_000
    high_severity = severity_score >= 7 and confidence >= 0.75
    return high_exposure or high_severity
```

**Audit log schema:**
```json
{
  "event_id": "uuid",
  "timestamp": "ISO8601",
  "disruption_summary": "string",
  "severity_score": 8,
  "escalated": true,
  "escalation_reason": "string",
  "alert_channel": "email|slack|both",
  "alert_sent_at": "ISO8601",
  "agent_decisions": {
    "agent1_confidence": 0.87,
    "agent2_chunks_retrieved": 5,
    "agent3_severity": 8,
    "agent4_recommendations_count": 4
  },
  "human_acknowledged": false
}
```

---

## 6. LangGraph State & Flow

### State Schema

```python
# graph/state.py
from typing import TypedDict, List, Optional, Dict, Any
from pydantic import BaseModel

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
    affected_suppliers: List[Dict]
    affected_routes: List[str]
    retrieved_chunks: List[str]
    retrieval_scores: List[float]

class ImpactAssessment(BaseModel):
    affected_suppliers: List[str]
    estimated_delay_days: Dict[str, int]
    financial_exposure_usd: Dict[str, float]
    at_risk_skus: List[str]
    severity_score: int
    reasoning_summary: str
    confidence: float

class AgentState(TypedDict):
    # Input
    query: str
    raw_news: List[Dict]
    
    # Agent outputs
    disruption_events: List[DisruptionEvent]
    supplier_context: Optional[SupplierContext]
    impact_assessment: Optional[ImpactAssessment]
    recommendations: List[Dict]
    
    # Control flow
    should_escalate: bool
    escalation_reason: str
    alert_sent: bool
    
    # Observability
    agent_trace: List[Dict]
    total_tokens_used: int
    total_cost_usd: float
    
    # Errors
    errors: List[str]
```

### Graph Definition

```python
# graph/graph.py
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
```

### Conditional Edge Logic

```python
# graph/edges.py
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
```

---

## 7. RAG Pipeline

### Document Ingestion

```python
# rag/ingestion.py
from langchain.document_loaders import PyPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
import pinecone

def ingest_documents(file_paths: list, index_name: str):
    """
    Ingest supplier docs, shipping route data, and historical events
    into Pinecone vector store.
    """
    all_docs = []
    
    for path in file_paths:
        if path.endswith('.pdf'):
            loader = PyPDFLoader(path)
        elif path.endswith('.csv'):
            loader = CSVLoader(path)
        docs = loader.load()
        all_docs.extend(docs)
    
    # Chunk documents
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(all_docs)
    
    # Add metadata
    for chunk in chunks:
        chunk.metadata['ingested_at'] = datetime.utcnow().isoformat()
    
    # Embed and store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = PineconeVectorStore.from_documents(
        chunks,
        embeddings,
        index_name=index_name
    )
    
    return vectorstore
```

### Hybrid Retrieval

```python
# rag/retriever.py
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

def retrieve_supplier_context(
    query: str,
    affected_regions: list,
    affected_industries: list,
    top_k: int = 5
) -> dict:
    """
    Hybrid retrieval with metadata filtering by region and industry.
    """
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = PineconeVectorStore(
        index_name="supply-chain-kb",
        embedding=embeddings
    )
    
    # Build metadata filter
    filter_dict = {}
    if affected_regions:
        filter_dict["region"] = {"$in": affected_regions}
    
    # Retrieve with scores
    results = vectorstore.similarity_search_with_score(
        query,
        k=top_k,
        filter=filter_dict if filter_dict else None
    )
    
    chunks = [doc.page_content for doc, score in results]
    scores = [score for doc, score in results]
    
    return {
        "chunks": chunks,
        "scores": scores,
        "avg_retrieval_score": sum(scores) / len(scores) if scores else 0
    }
```

---

## 8. Guardrails

```python
# guardrails/input_guard.py
from pydantic import BaseModel
from typing import Optional
import re

BLOCKED_PATTERNS = [
    r"ignore previous instructions",
    r"you are now",
    r"jailbreak",
    r"forget your",
]

OFF_TOPIC_KEYWORDS = [
    "recipe", "movie", "sports", "weather forecast",
    "joke", "poem", "dating"
]

class GuardrailResult(BaseModel):
    is_safe: bool
    reason: Optional[str] = None
    sanitized_input: Optional[str] = None

def check_input(user_input: str) -> GuardrailResult:
    # Check prompt injection
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            return GuardrailResult(
                is_safe=False,
                reason=f"Prompt injection pattern detected: {pattern}"
            )
    
    # Check off-topic
    lower_input = user_input.lower()
    for keyword in OFF_TOPIC_KEYWORDS:
        if keyword in lower_input:
            return GuardrailResult(
                is_safe=False,
                reason=f"Off-topic query detected. This system handles supply chain intelligence only."
            )
    
    # Sanitize
    sanitized = user_input.strip()[:2000]  # Limit length
    
    return GuardrailResult(is_safe=True, sanitized_input=sanitized)


# guardrails/output_guard.py
def check_output(llm_output: str) -> GuardrailResult:
    """
    Validate LLM output before returning to user.
    - Check for hallucinated company names
    - Check for PII leakage
    - Validate JSON structure
    """
    # Check for PII patterns
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'\b\d{10,}\b'
    
    if re.search(email_pattern, llm_output) or re.search(phone_pattern, llm_output):
        return GuardrailResult(
            is_safe=False,
            reason="PII detected in LLM output"
        )
    
    return GuardrailResult(is_safe=True, sanitized_input=llm_output)
```

---

## 9. Evaluation Layer (RAGAS)

```python
# evaluation/ragas_eval.py
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)
from datasets import Dataset
import json
from datetime import datetime

def run_ragas_evaluation(
    questions: list,
    answers: list,
    contexts: list,
    ground_truths: list
) -> dict:
    """
    Run RAGAS evaluation on RAG pipeline outputs.
    Returns metrics dict with precision, recall, faithfulness, relevancy.
    """
    eval_data = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    }
    
    dataset = Dataset.from_dict(eval_data)
    
    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        ]
    )
    
    metrics = {
        "faithfulness": float(result["faithfulness"]),
        "answer_relevancy": float(result["answer_relevancy"]),
        "context_precision": float(result["context_precision"]),
        "context_recall": float(result["context_recall"]),
        "evaluated_at": datetime.utcnow().isoformat(),
        "sample_size": len(questions)
    }
    
    # Store metrics for trending over time
    save_metrics(metrics)
    
    return metrics

def save_metrics(metrics: dict):
    """Append metrics to a JSONL file for trend analysis."""
    with open("evaluation/metrics_history.jsonl", "a") as f:
        f.write(json.dumps(metrics) + "\n")
```

### Evaluation Dataset (Build this manually — 20-30 Q&A pairs)

```python
# evaluation/eval_dataset.py
EVAL_DATASET = [
    {
        "question": "Which suppliers in Southeast Asia are affected by the port strike?",
        "ground_truth": "Suppliers in Vietnam and Thailand with shipping through Port of Singapore are affected.",
    },
    {
        "question": "What is the estimated delay for electronics components from Taiwan?",
        "ground_truth": "Estimated delay is 7-14 days due to typhoon disruption on trans-Pacific routes.",
    },
    # Add 20+ more pairs covering different disruption types
]
```

---

## 10. Observability (OpenTelemetry)

```python
# observability/tracer.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
import time

# Initialize tracer
provider = TracerProvider()
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("supply-chain-agent")

def trace_agent_call(agent_name: str, input_data: dict):
    """Context manager to trace individual agent calls."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(f"agent.{agent_name}") as span:
                start_time = time.time()
                span.set_attribute("agent.name", agent_name)
                span.set_attribute("agent.input_keys", str(list(input_data.keys())))
                
                result = func(*args, **kwargs)
                
                latency_ms = (time.time() - start_time) * 1000
                span.set_attribute("agent.latency_ms", latency_ms)
                span.set_attribute("agent.success", True)
                
                return result
        return wrapper
    return decorator


# observability/cost_tracker.py
import tiktoken

COST_PER_1K_TOKENS = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "text-embedding-3-small": {"input": 0.00002, "output": 0}
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    rates = COST_PER_1K_TOKENS.get(model, {"input": 0, "output": 0})
    cost = (input_tokens / 1000 * rates["input"]) + \
           (output_tokens / 1000 * rates["output"])
    return round(cost, 6)

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))
```

---

## 11. FastAPI Backend

```python
# api/main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from graph.graph import build_graph
from guardrails.input_guard import check_input
from observability.tracer import tracer

app = FastAPI(
    title="Supply Chain Disruption Intelligence API",
    description="Multi-agent AI system for supply chain risk monitoring",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

graph = build_graph()

class QueryRequest(BaseModel):
    query: str
    regions: Optional[list] = []
    industries: Optional[list] = []

class QueryResponse(BaseModel):
    disruption_events: list
    impact_assessment: dict
    recommendations: list
    escalated: bool
    severity_score: int
    total_cost_usd: float
    latency_ms: float

@app.post("/query", response_model=QueryResponse)
async def run_query(request: QueryRequest):
    # Guardrail check
    guard_result = check_input(request.query)
    if not guard_result.is_safe:
        raise HTTPException(status_code=400, detail=guard_result.reason)
    
    # Run graph
    import time
    start = time.time()
    
    result = graph.invoke({
        "query": guard_result.sanitized_input,
        "raw_news": [],
        "disruption_events": [],
        "agent_trace": [],
        "errors": []
    })
    
    latency_ms = (time.time() - start) * 1000
    
    return QueryResponse(
        disruption_events=[e.dict() for e in result.get("disruption_events", [])],
        impact_assessment=result.get("impact_assessment", {}).dict() if result.get("impact_assessment") else {},
        recommendations=result.get("recommendations", []),
        escalated=result.get("should_escalate", False),
        severity_score=result.get("impact_assessment", {}).severity_score if result.get("impact_assessment") else 0,
        total_cost_usd=result.get("total_cost_usd", 0),
        latency_ms=latency_ms
    )

@app.get("/alerts")
async def get_alerts(limit: int = 50):
    """Return recent escalated alerts from audit log."""
    # Query PostgreSQL audit log
    pass

@app.get("/metrics")
async def get_metrics():
    """Return RAGAS evaluation metrics and cost/latency trends."""
    pass

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 12. Streamlit / Plotly Dash Frontend

```python
# dashboard/app.py
import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Supply Chain Intelligence",
    page_icon="🚢",
    layout="wide"
)

st.title("🚢 Supply Chain Disruption Intelligence")
st.caption("Multi-agent AI system powered by LangGraph + RAG")

# Sidebar
with st.sidebar:
    st.header("Query Settings")
    regions = st.multiselect("Filter by Region", 
        ["Asia Pacific", "Europe", "North America", "Middle East", "South Asia"])
    industries = st.multiselect("Filter by Industry",
        ["Electronics", "Automotive", "Pharma", "Textiles", "Food & Beverage"])

# Main query
query = st.text_area(
    "Enter your supply chain query",
    placeholder="e.g. What is the impact of the Suez Canal blockage on European automotive suppliers?",
    height=100
)

if st.button("Analyze", type="primary"):
    with st.spinner("Running multi-agent analysis..."):
        response = requests.post(f"{API_BASE}/query", json={
            "query": query,
            "regions": regions,
            "industries": industries
        })
        
        if response.status_code == 200:
            data = response.json()
            
            # KPI Row
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Severity Score", f"{data['severity_score']}/10")
            col2.metric("Escalated", "Yes ⚠️" if data['escalated'] else "No ✅")
            col3.metric("Cost", f"${data['total_cost_usd']:.4f}")
            col4.metric("Latency", f"{data['latency_ms']:.0f}ms")
            
            # Disruption Events
            st.subheader("Detected Disruption Events")
            for event in data['disruption_events']:
                with st.expander(f"[{event['severity'].upper()}] {event['summary']}"):
                    st.json(event)
            
            # Impact Assessment
            st.subheader("Impact Assessment")
            if data['impact_assessment']:
                impact = data['impact_assessment']
                
                # Delay chart
                if impact.get('estimated_delay_days'):
                    delay_df = pd.DataFrame(
                        list(impact['estimated_delay_days'].items()),
                        columns=['Supplier', 'Delay (days)']
                    )
                    fig = px.bar(delay_df, x='Supplier', y='Delay (days)',
                                title="Estimated Delay by Supplier",
                                color='Delay (days)', color_continuous_scale='Reds')
                    st.plotly_chart(fig, use_container_width=True)
                
                st.write("**Reasoning:**", impact.get('reasoning_summary', ''))
            
            # Recommendations
            st.subheader("Recommendations")
            for i, rec in enumerate(data['recommendations'], 1):
                with st.expander(f"#{i} [{rec.get('timeline', '').upper()}] {rec.get('action', '')}"):
                    st.write("**Rationale:**", rec.get('rationale', ''))
                    st.write("**Expected Outcome:**", rec.get('expected_outcome', ''))
                    st.write("**Effort:**", rec.get('effort', ''))
        
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

# Metrics Dashboard (bottom section)
st.divider()
st.subheader("System Metrics")

metrics_col1, metrics_col2 = st.columns(2)

with metrics_col1:
    st.caption("RAG Evaluation Metrics (RAGAS)")
    # Load from metrics_history.jsonl
    try:
        metrics_data = []
        with open("evaluation/metrics_history.jsonl") as f:
            for line in f:
                metrics_data.append(json.loads(line))
        
        if metrics_data:
            latest = metrics_data[-1]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Faithfulness", f"{latest['faithfulness']:.2%}")
            m2.metric("Relevancy", f"{latest['answer_relevancy']:.2%}")
            m3.metric("Precision", f"{latest['context_precision']:.2%}")
            m4.metric("Recall", f"{latest['context_recall']:.2%}")
    except FileNotFoundError:
        st.info("Run evaluation to see metrics")

with metrics_col2:
    st.caption("Recent Alerts")
    alerts_response = requests.get(f"{API_BASE}/alerts?limit=5")
    if alerts_response.status_code == 200:
        alerts = alerts_response.json()
        for alert in alerts:
            st.warning(f"⚠️ {alert.get('disruption_summary', '')}")
```

---

## 13. AWS Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Expose ports
EXPOSE 8000 8501

# Start script
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
```

### start.sh

```bash
#!/bin/bash
# Start FastAPI backend
uvicorn api.main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit frontend
streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0 &

# Wait for any process to exit
wait -n

# Exit with the status of the process that exited first
exit $?
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - NEWS_API_KEY=${NEWS_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - postgres
    
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: supply_chain
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### AWS EC2 Deployment Steps

```bash
# 1. Launch EC2 instance (t2.micro free tier)
# AMI: Ubuntu 22.04 LTS
# Security Group: open ports 22, 8000, 8501

# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Install Docker
sudo apt update
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker ubuntu

# 4. Clone your repo
git clone https://github.com/yourusername/supply-chain-agent.git
cd supply-chain-agent

# 5. Set environment variables
cp .env.example .env
nano .env  # Fill in your API keys

# 6. Build and run
docker-compose up -d

# 7. Check status
docker-compose ps
docker-compose logs -f app
```

---

## 14. CI/CD with GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest tests/ -v
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          PINECONE_API_KEY: ${{ secrets.PINECONE_API_KEY }}
```

```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to EC2
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ubuntu
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            cd supply-chain-agent
            git pull origin main
            docker-compose down
            docker-compose up -d --build
```

---

## 15. Data Sources

### Public Datasets (Free)
| Dataset | Source | Use |
|---|---|---|
| Olist E-commerce Supply Chain | Kaggle | Supplier/order relationships |
| Supply Chain Security Dataset | Kaggle | Historical disruption events |
| Global Shipping Routes | OpenStreetMap / MarineTraffic | Route data |
| UN Comtrade | UN | Trade flow data |

### Live APIs
| API | Free Tier | Use |
|---|---|---|
| NewsAPI | 100 req/day | Live news ingestion |
| SerpAPI | 100 req/month | Google News search |
| Yahoo Finance (yfinance) | Unlimited | Market impact |

### Synthetic Data (Generate with Python)
```python
# Generate synthetic supplier dataset
import pandas as pd
import numpy as np

suppliers = pd.DataFrame({
    'supplier_id': range(1, 101),
    'name': [f"Supplier_{i}" for i in range(1, 101)],
    'country': np.random.choice(['China', 'Vietnam', 'Taiwan', 'India', 'Germany'], 100),
    'industry': np.random.choice(['Electronics', 'Automotive', 'Pharma', 'Textiles'], 100),
    'tier': np.random.choice([1, 2, 3], 100, p=[0.2, 0.5, 0.3]),
    'annual_spend_usd': np.random.randint(100_000, 10_000_000, 100),
    'primary_port': np.random.choice(['Shanghai', 'Singapore', 'Rotterdam', 'Mumbai'], 100),
    'lead_time_days': np.random.randint(7, 45, 100),
    'risk_score': np.random.uniform(0.1, 0.9, 100).round(2)
})

suppliers.to_csv('data/supplier_data.csv', index=False)
```

---

## 16. Environment Variables

```bash
# .env.example

# LLM
OPENAI_API_KEY=sk-...

# Vector Store
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=supply-chain-kb
PINECONE_ENVIRONMENT=gcp-starter

# News APIs
NEWS_API_KEY=...
SERP_API_KEY=...

# Database
DATABASE_URL=postgresql://admin:password@localhost:5432/supply_chain

# Observability
AGENTOPS_API_KEY=...
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# Alerts
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=...
SLACK_WEBHOOK_URL=https://hooks.slack.com/...

# AWS (for deployment)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=ap-south-1
S3_BUCKET_NAME=supply-chain-docs
```

---

## 17. Resume Bullets

Once built, use bullets like these (fill in your actual numbers):

**Project Title:** Supply Chain Disruption Intelligence Agent

> Designed and deployed a 5-agent LangGraph orchestration system that monitors live supply chain disruption signals, performs RAG-based supplier impact analysis, and generates prioritized recommendations with human escalation logic.

**Bullet 1 — Architecture:**
> Orchestrated 5 specialized LangGraph agents (News Monitor, RAG Retrieval, Impact Assessor, Recommendation, Escalation) with conditional state routing achieving end-to-end query resolution in under 4 seconds.

**Bullet 2 — RAG & Evaluation:**
> Built hybrid RAG pipeline over multi-source supplier knowledge base using Pinecone vector store; implemented RAGAS evaluation achieving 84% context precision and 91% answer faithfulness across 30-query evaluation set.

**Bullet 3 — Observability:**
> Instrumented full agent pipeline with OpenTelemetry tracing and AgentOps monitoring, tracking per-agent latency, token cost, and decision audit trail; average cost per query: $0.003.

**Bullet 4 — Deployment:**
> Containerized with Docker and deployed on AWS EC2 with FastAPI backend and Streamlit dashboard; automated deployment via GitHub Actions CI/CD pipeline triggered on main branch merge.

---

*Good luck. Build it fast, deploy it real, measure everything.*

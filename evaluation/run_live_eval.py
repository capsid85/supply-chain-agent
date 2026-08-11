import os
import sys
from dotenv import load_dotenv

# Ensure the root project directory is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from graph.graph import build_graph
from evaluation.eval_dataset import EVAL_DATASET
from evaluation.ragas_eval import run_ragas_evaluation

def run_live_eval():
    print("Initializing LangGraph pipeline for live evaluation...")
    graph = build_graph()
    
    questions = []
    answers = []
    contexts = []
    ground_truths = []
    
    # Process all 22 questions through the actual graph
    total_q = len(EVAL_DATASET)
    print(f"Sending {total_q} queries through the LangGraph pipeline...")
    
    for idx, item in enumerate(EVAL_DATASET, 1):
        q = item["question"]
        gt = item["ground_truth"]
        
        print(f"[{idx}/{total_q}] Processing query: '{q}'...")
        
        try:
            # Invoke actual pipeline
            result = graph.invoke({
                "query": q,
                "raw_news": [],
                "disruption_events": [],
                "supplier_context": None,
                "impact_assessment": None,
                "recommendations": [],
                "should_escalate": False,
                "escalation_reason": "",
                "alert_sent": False,
                "agent_trace": [],
                "total_tokens_used": 0,
                "total_cost_usd": 0.0,
                "errors": []
            })
            
            # Combine the pipeline outputs to represent the final system answer
            events = result.get("disruption_events", [])
            assessment = result.get("impact_assessment")
            recs = result.get("recommendations", [])
            
            event_summary = events[0].summary if events else ""
            impact_summary = assessment.reasoning_summary if assessment else ""
            rec_summary = "; ".join([r.get("action", "") for r in recs]) if recs else ""
            
            full_answer = f"Disruption: {event_summary}. Impact: {impact_summary}. Mitigation Actions: {rec_summary}."
            
            # Extract retrieved contexts
            supplier_context = result.get("supplier_context")
            retrieved_chunks = supplier_context.retrieved_chunks if supplier_context else []
            
            if not retrieved_chunks:
                retrieved_chunks = ["No context retrieved."]
                
            questions.append(q)
            answers.append(full_answer)
            contexts.append(retrieved_chunks)
            ground_truths.append(gt)
            
            # Rate limit/delay between OpenAI calls
            import time
            time.sleep(1.5)
            
        except Exception as e:
            print(f"Error processing query '{q}': {e}")
            
    if not questions:
        print("Error: No queries completed successfully.")
        return
        
    print("\nRunning RAGAS evaluation over the actual outputs...")
    metrics = run_ragas_evaluation(questions, answers, contexts, ground_truths)
    
    print("\n================ LIVE EVALUATION RESULTS ================")
    print(f"Answer Relevancy:   {metrics.get('answer_relevancy', 0):.2%}")
    print(f"Sample Size:        {metrics.get('sample_size', 0)} queries")
    print(f"Evaluated At:       {metrics.get('evaluated_at')}")
    print("=========================================================")

if __name__ == "__main__":
    run_live_eval()

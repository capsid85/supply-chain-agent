import os
import json
import re
from openai import OpenAI

def call_llm_json(prompt: str, system_prompt: str = "You are a supply chain intelligence assistant.", response_model_name: str = "") -> dict:
    """
    Calls OpenAI LLM if key is present, otherwise falls back to a smart mock response generator.
    Ensures response is returned as a parsed dictionary.
    """
    use_local = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    # 1. Groq Cloud execution
    if groq_api_key and not use_local:
        try:
            client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=groq_api_key
            )
            # Use llama-3.3-70b-versatile or llama-3.1-8b-instant.
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"Groq API call failed ({e}). Trying 8b model...")
            try:
                # Fallback to 8b model
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1
                )
                content = response.choices[0].message.content
                return json.loads(content)
            except Exception as e8b:
                print(f"Groq 8b API call failed ({e8b}). Falling back to next available provider.")

    # 2. Local Ollama LLM execution
    if use_local:
        try:
            import requests
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": "llama3",
                "prompt": prompt,
                "system": system_prompt,
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.1
                }
            }
            res = requests.post(url, json=payload, timeout=60)
            if res.status_code == 200:
                resp_json = res.json()
                content = resp_json.get("response", "")
                return json.loads(content)
        except Exception as e:
            print(f"Local Ollama call failed ({e}). Falling back to mock generator.")

    # 3. OpenAI Production execution
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and not use_local and not groq_api_key:
        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"OpenAI call failed ({e}). Falling back to simulated response.")
    
    # Smart Mock Generator
    # We parse the prompt or query keywords to build a logical output
    prompt_lower = prompt.lower()
    
    # 1. NEWS MONITOR MOCK
    if "classify this article" in prompt_lower or "news monitor" in prompt_lower or response_model_name == "DisruptionEvent":
        # Check keywords
        title = "Global Supply Chain Congestion Alert"
        summary = "Unforeseen logistics constraints are causing delays across multiple transit corridors."
        disruption_type = "logistics"
        severity = "medium"
        regions = ["Asia Pacific"]
        industries = ["Electronics"]
        confidence = 0.85
        
        if "taiwan" in prompt_lower or "semiconductor" in prompt_lower or "typhoon" in prompt_lower:
            title = "Super Typhoon Gaemi Forces Port & Factory Shutdowns in Taiwan"
            summary = "Heavy rains and high winds from Typhoon Gaemi lead to temporary closures of critical electronics fabs and Kaohsiung port operations."
            disruption_type = "weather"
            severity = "high"
            regions = ["Asia Pacific"]
            industries = ["Electronics", "Automotive"]
            confidence = 0.95
        elif "strike" in prompt_lower or "labor" in prompt_lower or "union" in prompt_lower:
            title = "West Coast Port Labor Dispute Triggers Work Stoppages"
            summary = "Union workers at major West Coast ports declare strike action, stalling cargo loading and creating a logistics bottleneck."
            disruption_type = "labor"
            severity = "high"
            regions = ["North America"]
            industries = ["Electronics", "Automotive", "Pharma", "Textiles"]
            confidence = 0.90
        elif "suez" in prompt_lower or "canal" in prompt_lower or "red sea" in prompt_lower:
            title = "Red Sea Security Escalation Forces Suez Canal Diversions"
            summary = "Geopolitical tensions and threats to cargo ships in the Bab el-Mandeb strait lead carriers to reroute around Africa."
            disruption_type = "geopolitical"
            severity = "critical"
            regions = ["Middle East", "Europe"]
            industries = ["Electronics", "Automotive", "Pharma"]
            confidence = 0.98
        elif "germany" in prompt_lower or "europe" in prompt_lower:
            title = "Industrial Strike Halts Production Lines in Germany"
            summary = "Geopolitical and labor changes lead to critical parts shortage at automotive manufacturing facilities in Stuttgart."
            disruption_type = "labor"
            severity = "high"
            regions = ["Europe"]
            industries = ["Automotive"]
            confidence = 0.88

        return {
            "title": title,
            "content": f"Full report on: {title}. {summary}",
            "disruption_type": disruption_type,
            "severity": severity,
            "affected_regions": regions,
            "affected_industries": industries,
            "confidence": confidence,
            "summary": summary
        }

    # 2. RAG AGENT MOCK
    elif "knowledge retrieval" in prompt_lower or response_model_name == "SupplierContext":
        return {
            "affected_suppliers": [
                {"supplier_id": "SUP_001", "name": "Acme Electronics (Taiwan)", "risk_level": "high"},
                {"supplier_id": "SUP_004", "name": "V-Tech Semiconductors (Taiwan)", "risk_level": "high"}
            ],
            "affected_routes": ["Kaohsiung to Los Angeles", "Shanghai to Seattle"],
            "inventory_implications": "Safety stock of microcontrollers is estimated to last 12 days. Lead times will expand by 14 days.",
            "flagged_gaps": "Tier-3 raw material dependencies for wafer supply are unverified."
        }

    # 3. IMPACT ASSESSOR MOCK
    elif "impact risk analyst" in prompt_lower or "impactassessment" in prompt_lower or response_model_name == "ImpactAssessment":
        severity_score = 6
        delay = 10
        exposure = {"low": 150000.0, "high": 600000.0}
        
        if "critical" in prompt_lower or "suez" in prompt_lower:
            severity_score = 9
            delay = 20
            exposure = {"low": 800000.0, "high": 2500000.0}
        elif "high" in prompt_lower or "typhoon" in prompt_lower or "strike" in prompt_lower:
            severity_score = 7
            delay = 14
            exposure = {"low": 300000.0, "high": 1200000.0}

        return {
            "affected_suppliers": ["Acme Electronics (Taiwan)", "V-Tech Semiconductors (Taiwan)"],
            "estimated_delay_days": {
                "Acme Electronics (Taiwan)": delay,
                "V-Tech Semiconductors (Taiwan)": delay + 4
            },
            "financial_exposure_usd": exposure,
            "at_risk_skus": ["SKU-MCU-8051", "SKU-DSP-GEN3", "SKU-AUTO-ECU2"],
            "severity_score": severity_score,
            "reasoning_summary": f"Disruption restricts transit through main shipping lanes, extending lead times to {delay} - {delay+4} days. The financial exposure is driven by downstream manufacturing idle time and potential SLA penalties.",
            "confidence": 0.88
        }

    # 4. RECOMMENDATION AGENT MOCK
    elif "recommendation" in prompt_lower or response_model_name == "Recommendations":
        # Let's return standard list of actions
        return [
            {
                "action": "Activate Secondary Semiconductor Supplier",
                "rationale": "Mitigates primary supply halt in Taiwan by shifting allocation to US-based GlobalFoundries.",
                "timeline": "short-term (1-7 days)",
                "effort": "medium",
                "expected_outcome": "Restores 40% of standard production supply, reducing delay impact.",
                "alternative_suppliers": "GlobalFoundries (USA) - Pros: reliable, low transit risk; Cons: +15% cost premium."
            },
            {
                "action": "Reroute Ocean Cargo to East Coast Ports",
                "rationale": "Bypasses strike-ridden West Coast ports by shifting routes through Panama Canal to Savannah port.",
                "timeline": "immediate (0-24h)",
                "effort": "high",
                "expected_outcome": "Avoids port backlog, though increases ocean transit time by 6 days.",
                "alternative_suppliers": "Maersk Logistics Alternative - Pros: guaranteed berthing; Cons: high spot rate pricing."
            },
            {
                "action": "Increase Safety Stock Thresholds",
                "rationale": "Buffers against future weather and geopolitical disruptions in the APAC region.",
                "timeline": "medium-term (1-4 weeks)",
                "effort": "low",
                "expected_outcome": "Increases buffer inventory from 14 to 30 days.",
                "alternative_suppliers": "N/A"
            }
        ]

    # Standard fallback
    return {"message": "Simulated default AI completion output.", "status": "success"}

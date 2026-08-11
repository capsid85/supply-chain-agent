import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import os
from datetime import datetime

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

# Custom styling for premium aesthetic
st.set_page_config(
    page_title="Supply Chain Disruption Intelligence",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF4B4B, #FF8F00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #7A869A;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #0E1117;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.5rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #F8FAFC;
        border-bottom: 2px solid #1E293B;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚢 Supply Chain Disruption Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Autonomous multi-agent LangGraph system executing early-warning detection, RAG supplier analysis, and risk mitigations.</div>', unsafe_allow_html=True)

# Sidebar for Filters
with st.sidebar:
    st.header("🔍 Control Panel")
    st.markdown("Filter incoming signal scopes before dispatching multi-agent query.")
    
    regions = st.multiselect(
        "Geographic Focus", 
        ["Asia Pacific", "Europe", "North America", "Middle East", "South Asia"],
        default=[]
    )
    
    industries = st.multiselect(
        "Sectors / Industries",
        ["Electronics", "Automotive", "Pharma", "Textiles", "Food & Beverage"],
        default=[]
    )
    
    st.divider()
    st.caption("🤖 **Agent Deployment Status**")
    st.success("News Monitor Agent: Active")
    st.success("RAG Knowledge Agent: Active")
    st.success("Impact Assessor Agent: Active")
    st.success("Mitigation Advisor: Active")
    st.success("Escalation Gatekeeper: Active")

# Main Input Section
st.subheader("💡 Trigger Disruption Analysis")
query = st.text_area(
    "Query input (simulates an intelligence alert, news flash, or risk inquiry)",
    placeholder="e.g., What is the impact of Typhoon Gaemi on Taiwan electronics suppliers and shipping routes to LA?",
    height=80
)

col_run, col_clear = st.columns([1, 8])
run_analysis = col_run.button("Run Agents", type="primary")

if run_analysis and query.strip():
    with st.spinner("Executing LangGraph multi-agent pipeline..."):
        try:
            response = requests.post(f"{API_BASE}/query", json={
                "query": query,
                "regions": regions,
                "industries": industries
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # KPI Section
                st.markdown('<div class="section-header">📊 Real-time Execution KPI</div>', unsafe_allow_html=True)
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                
                severity = data['severity_score']
                severity_color = "#EF4444" if severity >= 7 else ("#F59E0B" if severity >= 4 else "#10B981")
                
                kpi1.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: {severity_color}">{severity}/10</div>
                    <div class="metric-label">Severity Score</div>
                </div>
                """, unsafe_allow_html=True)
                
                esc_status = "YES ⚠️" if data['escalated'] else "NO ✅"
                esc_color = "#EF4444" if data['escalated'] else "#10B981"
                kpi2.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: {esc_color}">{esc_status}</div>
                    <div class="metric-label">Escalation Triggered</div>
                </div>
                """, unsafe_allow_html=True)
                
                kpi3.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">${data['total_cost_usd']:.4f}</div>
                    <div class="metric-label">LLM Run Cost</div>
                </div>
                """, unsafe_allow_html=True)
                
                kpi4.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{data['latency_ms']:.0f}ms</div>
                    <div class="metric-label">End-to-End Latency</div>
                </div>
                """, unsafe_allow_html=True)

                # Layout tabs
                tab1, tab2, tab3 = st.tabs(["📢 Detected Events", "🛡️ Supplier Impact & Route Delays", "🛠️ Action Recommendations"])
                
                with tab1:
                    st.markdown("### classified signals")
                    for event in data.get('disruption_events', []):
                        st.info(f"**[{event['disruption_type'].upper()}] {event['title']}** (Confidence: {event['confidence']:.2%})")
                        st.markdown(f"**Summary:** {event['summary']}")
                        st.caption(f"Regions: {', '.join(event['affected_regions'])} | Industries: {', '.join(event['affected_industries'])}")
                
                with tab2:
                    impact = data.get('impact_assessment', {})
                    if impact:
                        st.markdown("### Downstream Exposure Analysis")
                        st.write(f"**Reasoning Summary:** {impact.get('reasoning_summary')}")
                        
                        # Financial Exposure Chart
                        fin_exp = impact.get('financial_exposure_usd', {})
                        if fin_exp:
                            fig_fin = go.Figure(data=[
                                go.Bar(name='Min Exposure', x=['Exposure Range'], y=[fin_exp.get('low', 0)], marker_color='#F59E0B'),
                                go.Bar(name='Max Exposure', x=['Exposure Range'], y=[fin_exp.get('high', 0)], marker_color='#EF4444')
                            ])
                            fig_fin.update_layout(title="Estimated Downstream Financial Exposure (USD)", barmode='group', template='plotly_dark')
                            st.plotly_chart(fig_fin, use_container_width=True)
                            
                        # Delays Chart
                        delays = impact.get('estimated_delay_days', {})
                        if delays:
                            df_delays = pd.DataFrame(list(delays.items()), columns=["Supplier", "Delay Days"])
                            fig_delays = px.bar(
                                df_delays, 
                                x="Supplier", 
                                y="Delay Days", 
                                color="Delay Days",
                                title="Estimated Route & Logistics Delay by Supplier",
                                color_continuous_scale="Reds",
                                template="plotly_dark"
                            )
                            st.plotly_chart(fig_delays, use_container_width=True)
                            
                        st.write("**Impacted SKUs:**")
                        st.write(", ".join([f"`{sku}`" for sku in impact.get('at_risk_skus', [])]))
                    else:
                        st.info("No downstream supplier impact assessed for low-severity signals.")
                        
                with tab3:
                    st.markdown("### Actionable Recommendations")
                    recs = data.get('recommendations', [])
                    if recs:
                        for idx, rec in enumerate(recs, 1):
                            with st.expander(f"Recommendation #{idx}: {rec.get('action')}"):
                                st.markdown(f"**Rationale:** {rec.get('rationale')}")
                                st.markdown(f"**Expected Outcome:** {rec.get('expected_outcome')}")
                                st.markdown(f"**Timeline:** `{rec.get('timeline')}` | **Effort Level:** `{rec.get('effort')}`")
                                if rec.get('alternative_suppliers'):
                                    st.warning(f"**Alternative Suppliers:** {rec.get('alternative_suppliers')}")
                    else:
                        st.info("No high-priority recommendations compiled (Signal severity resolved under threshold).")
            else:
                st.error(f"Error executing analysis: {response.json().get('detail', 'Unknown error occurred')}")
        except Exception as e:
            st.error(f"Failed to communicate with FastAPI backend: {e}")

# Lower metrics dashboard
st.markdown('<div class="section-header">📈 System Metrics & Audit Trail</div>', unsafe_allow_html=True)
metrics_col1, metrics_col2 = st.columns(2)

with metrics_col1:
    st.markdown("### RAG Evaluation Performance (RAGAS)")
    # Request latest metrics
    try:
        metrics_res = requests.get(f"{API_BASE}/metrics", timeout=5)
        if metrics_res.status_code == 200:
            metrics_data = metrics_res.json()
            eval_m = metrics_data.get("evaluation_metrics", {})
            
            m_col1, m_col2 = st.columns(2)
            m_col1.metric("Faithfulness (RAGAS)", f"{eval_m.get('faithfulness', 0):.1%}")
            m_col1.metric("Answer Relevancy (RAGAS)", f"{eval_m.get('answer_relevancy', 0):.1%}")
            m_col2.metric("Context Precision", f"{eval_m.get('context_precision', 0):.1%}")
            m_col2.metric("Context Recall", f"{eval_m.get('context_recall', 0):.1%}")
            
            sys_m = metrics_data.get("system_usage", {})
            st.caption(f"System usage stats: Total historical queries analyzed: **{sys_m.get('total_queries_run', 0)}** | Escalation trigger rate: **{sys_m.get('escalation_rate', 0):.1%}**")
        else:
            st.info("Start the FastAPI backend to display active system metrics.")
    except Exception:
        st.info("FastAPI backend is offline. Start the server to load real-time RAGAS analytics.")

with metrics_col2:
    st.markdown("### Escalated Alerts Log")
    try:
        alerts_res = requests.get(f"{API_BASE}/alerts?limit=5", timeout=5)
        if alerts_res.status_code == 200:
            alerts = alerts_res.json()
            if alerts:
                for alert in alerts:
                    # Render warning box
                    ack_label = "Acknowledged ✅" if alert.get("human_acknowledged") else "Acknowledge 🛎️"
                    
                    c_text, c_btn = st.columns([4, 1])
                    c_text.warning(f"**[{alert['timestamp'][:19]}] Severity {alert['severity_score']}/10** - {alert['disruption_summary']}\n*Reason: {alert['escalation_reason']}*")
                    
                    if not alert.get("human_acknowledged"):
                        if c_btn.button(ack_label, key=alert["event_id"]):
                            requests.post(f"{API_BASE}/alerts/{alert['event_id']}/acknowledge")
                            st.rerun()
                    else:
                        c_btn.markdown("<p style='color:#10B981; margin-top:15px;'>Acknowledged</p>", unsafe_allow_html=True)
            else:
                st.info("No escalated alerts recorded in database logs.")
        else:
            st.info("FastAPI backend is offline. Cannot query alert logs.")
    except Exception:
        st.info("FastAPI backend is offline. Cannot load escalated alerts database feed.")

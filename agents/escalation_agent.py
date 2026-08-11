import os
import uuid
import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import requests
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

from graph.state import DisruptionEvent, SupplierContext, ImpactAssessment
from observability.tracer import trace_agent_call

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./supply_chain.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    disruption_summary = Column(String)
    severity_score = Column(Integer)
    escalated = Column(Boolean)
    escalation_reason = Column(String)
    alert_channel = Column(String)
    alert_sent_at = Column(String, nullable=True)
    agent_decisions = Column(Text) # JSON stringified
    human_acknowledged = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

def should_escalate(severity_score: int, confidence: float, financial_exposure: dict, events: list) -> tuple:
    """
    Decide whether to escalate.
    Returns (should_escalate_bool, reason_string)
    """
    high_exposure = financial_exposure.get('high', 0) > 1_000_000
    high_severity = severity_score >= 7 and confidence >= 0.75
    
    critical_disruption = False
    for event in events:
        if event.severity.lower() == 'critical':
            critical_disruption = True
            break
            
    reasons = []
    if high_exposure:
        reasons.append(f"Financial exposure high estimate (${financial_exposure.get('high'):,}) exceeds $1M threshold")
    if high_severity:
        reasons.append(f"Severity score ({severity_score}/10) is >= 7 and assessment confidence ({confidence:.2f}) is >= 0.75")
    if critical_disruption:
        reasons.append("Critical disruption severity flagged on input event")

    if reasons:
        return True, " & ".join(reasons)
    return False, "Does not meet escalation thresholds"

def send_slack_alert(webhook_url: str, message: str) -> bool:
    try:
        response = requests.post(webhook_url, json={"text": message}, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send Slack alert: {e}")
        return False

def send_email_alert(subject: str, body: str) -> bool:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_host or not smtp_user or not smtp_password:
        return False
        
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = smtp_user # Send to self for demo purposes
        
        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send Email alert: {e}")
        return False

@trace_agent_call("escalation_agent", {"input": "impact_assessment"})
def run_escalation_agent(
    events: list,
    context: SupplierContext,
    assessment: ImpactAssessment,
    recs: list
) -> dict:
    """
    Evaluates impact assessment and recommendations to determine escalation, dispatches alerts, and writes audit logs.
    """
    severity_score = assessment.severity_score if assessment else 0
    confidence = assessment.confidence if assessment else 0.0
    financial_exposure = assessment.financial_exposure_usd if assessment else {}

    escalate, reason = should_escalate(severity_score, confidence, financial_exposure, events)
    
    alert_channel = "none"
    alert_sent_at = None
    alert_sent = False

    if escalate:
        alert_body = (
            f"⚠️ SUPPLY CHAIN ESCALATION ALERT ⚠️\n\n"
            f"Reason: {reason}\n"
            f"Severity Score: {severity_score}/10\n"
            f"Estimated Delays: {assessment.estimated_delay_days}\n"
            f"Financial Exposure: Low: ${financial_exposure.get('low', 0):,}, High: ${financial_exposure.get('high', 0):,}\n"
            f"SKUs Impacted: {assessment.at_risk_skus}\n\n"
            f"Mitigation Actions Recommended:\n"
        )
        for r in recs[:3]:
            alert_body += f"- [{r.get('timeline')}] {r.get('action')}: {r.get('rationale')}\n"

        slack_url = os.getenv("SLACK_WEBHOOK_URL")
        email_user = os.getenv("SMTP_USER")
        
        channels = []
        if slack_url:
            slack_ok = send_slack_alert(slack_url, alert_body)
            if slack_ok:
                channels.append("slack")
        if email_user:
            email_ok = send_email_alert("Supply Chain Disruption Escalation", alert_body)
            if email_ok:
                channels.append("email")
                
        if channels:
            alert_channel = "|".join(channels)
            alert_sent_at = datetime.utcnow().isoformat()
            alert_sent = True
        else:
            print("Alert not sent: alert channel credentials not configured.")

    # Write audit log
    event_id = str(uuid.uuid4())
    disruption_summary = events[0].summary if events else "Unknown Disruption"
    
    decisions = {
        "agent1_confidence": float(events[0].confidence) if events else 0.0,
        "agent2_chunks_retrieved": len(context.retrieved_chunks) if context else 0,
        "agent3_severity": severity_score,
        "agent4_recommendations_count": len(recs)
    }

    db_log = AuditLog(
        id=event_id,
        timestamp=datetime.utcnow(),
        disruption_summary=disruption_summary,
        severity_score=severity_score,
        escalated=escalate,
        escalation_reason=reason,
        alert_channel=alert_channel,
        alert_sent_at=alert_sent_at,
        agent_decisions=json.dumps(decisions),
        human_acknowledged=False
    )

    db = SessionLocal()
    try:
        db.add(db_log)
        db.commit()
        print(f"Audit log saved to database. Event ID: {event_id}")
    except Exception as e:
        db.rollback()
        print(f"Failed to write audit log to database: {e}")
    finally:
        db.close()

    return {
        "should_escalate": escalate,
        "escalation_reason": reason,
        "alert_sent": alert_sent
    }

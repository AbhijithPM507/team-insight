from app.services.config_loader import load_config
from app.services.rule_engine import run_rule_engine


def run_full_analysis(ai_output: dict, domain: str):

    config = load_config(domain)

    rule_results = run_rule_engine(ai_output, config)

    return {
        "analysis": {
            "conversation_summary": ai_output.get("summary"),
            "detected_domain": ai_output.get("detected_domain"),
            "primary_intent": ai_output.get("primary_intent"),
            "ai_risk_score": ai_output.get("risk_score"),
            "key_topics": ai_output.get("key_topics"),
            "agent_analysis": ai_output.get("agent_analysis"),
            "customer_analysis": ai_output.get("customer_analysis"),
            "resolution_status": ai_output.get("resolution_status"),
            "language": ai_output.get("language")
        },
        "risk_assessment": {
            "rule_based_risk_score": rule_results["risk_score"],
            "risk_level": rule_results["risk_level"],
            "escalation_required": rule_results["escalation_required"],
            "risk_contributors": rule_results["risk_contributors"]
        },
        "compliance": rule_results["compliance"],
        "topic_control": rule_results["topic_control"],
        "outcome": rule_results["outcome"],
        "domain_used_for_rules": domain
    }
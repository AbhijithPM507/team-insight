from app.services.config_loader import load_config
from app.services.rule_engine import run_rule_engine


def run_full_analysis(ai_output: dict, domain: str):
    """
    Orchestrates full backend analysis:
    - Loads domain configuration
    - Runs rule engine
    - Returns structured enterprise-ready response
    """

    # 🔹 Load domain configuration
    config = load_config(domain)

    # 🔹 Run rule engine (risk + compliance + outcome)
    rule_results = run_rule_engine(ai_output, config)

    # 🔹 Build final structured response
    return {
        "analysis": {
            "conversation_summary": ai_output.get("summary", ""),
            "sentiment_overall": ai_output.get("sentiment", ""),
            "primary_intents": ai_output.get("intents", []),
        },
        "risk_assessment": {
            "risk_score": rule_results["risk_score"],
            "risk_level": rule_results["risk_level"],
            "escalation_required": rule_results["escalation_required"],
            "risk_contributors": rule_results["risk_contributors"]
        },
        "compliance": rule_results["compliance"],
        "outcome": rule_results["outcome"],
        "domain": domain
    }
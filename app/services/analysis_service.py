from app.services.config_loader import load_config
from app.services.rule_engine import run_rule_engine
from copy import deepcopy


def run_full_analysis(ai_output: dict, domain: str, client_config: dict = None):
    """
    Orchestrates full intelligence processing.
    - Loads base domain config
    - Merges company-level overrides (if provided)
    - Executes rule engine
    - Builds final structured response
    """

    # 🔹 1. Load base domain configuration
    base_config = load_config(domain)

    # 🔹 2. Merge with client-level overrides (if any)
    final_config = _merge_configs(base_config, client_config)

    # 🔹 3. Run deterministic rule engine
    rule_results = run_rule_engine(ai_output, final_config)

    # 🔹 4. Build final enterprise response
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
            "rule_based_risk_score": rule_results.get("risk_score"),
            "risk_level": rule_results.get("risk_level"),
            "escalation_required": rule_results.get("escalation_required"),
            "risk_contributors": rule_results.get("risk_contributors")
        },
        "compliance": rule_results.get("compliance"),
        "topic_control": rule_results.get("topic_control"),
        "outcome": rule_results.get("outcome"),
        "domain_used_for_rules": domain
    }


# ---------------------------------------------------------
# 🔹 Helper: Merge Base Config with Client Overrides
# ---------------------------------------------------------

def _merge_configs(base_config: dict, client_config: dict | None):
    """
    Allows dynamic company-level rule overrides.
    Client config overrides domain defaults.
    """

    if not client_config:
        return base_config

    # Deep copy to avoid mutating base config
    merged = deepcopy(base_config)

    for key, value in client_config.items():
        if isinstance(value, dict) and key in merged:
            # Merge nested dictionaries
            merged[key].update(value)
        else:
            # Override or add new key
            merged[key] = value

    return merged
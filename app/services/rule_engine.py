from app.services.risk_scorer import classify_risk


def detect_compliance_violations(summary: str, config: dict):
    """
    Detect compliance violations based on forbidden phrases
    defined in domain configuration.
    """

    violations = []
    rules = config.get("compliance_rules", {})

    forbidden_phrases = rules.get("forbidden_promises", [])

    for phrase in forbidden_phrases:
        if phrase.lower() in summary.lower():
            violations.append({
                "type": "forbidden_promise",
                "phrase": phrase,
                "severity": "HIGH"
            })

    return violations


def classify_outcome(ai_output: dict, risk_level: str, config: dict):
    """
    Classifies call outcome based on domain-specific outcome rules.
    """

    summary = ai_output.get("summary", "").lower()
    rules = config.get("outcome_rules", {})

    # Escalated
    if any(word in summary for word in rules.get("escalated_keywords", [])) \
            or risk_level == "HIGH":
        return {
            "type": "ESCALATED",
            "reason": "Escalation keyword detected or high risk"
        }

    # Customer churn
    if any(word in summary for word in rules.get("churn_keywords", [])):
        return {
            "type": "CUSTOMER_CHURN_RISK",
            "reason": "Churn-related keyword detected"
        }

    # Resolved
    if any(word in summary for word in rules.get("resolved_keywords", [])):
        return {
            "type": "RESOLVED",
            "reason": "Resolution keyword detected"
        }

    # Follow-up required
    if any(word in summary for word in rules.get("followup_keywords", [])):
        return {
            "type": "FOLLOW_UP_REQUIRED",
            "reason": "Follow-up keyword detected"
        }

    return {
        "type": "COMPLETED",
        "reason": "No escalation or churn detected"
    }


def run_rule_engine(ai_output: dict, config: dict):
    """
    Main rule engine that:
    - Calculates risk score
    - Detects compliance violations
    - Classifies outcome
    """

    sentiment = ai_output.get("sentiment", "")
    intents = ai_output.get("intents", [])
    summary = ai_output.get("summary", "")

    risk_score = 0
    risk_contributors = {}

    # 🔹 Sentiment trigger
    negative_threshold = config.get("risk_triggers", {}).get(
        "negative_sentiment_threshold", ""
    )

    if sentiment == negative_threshold:
        risk_score += 3
        risk_contributors["sentiment_risk"] = 3
    else:
        risk_contributors["sentiment_risk"] = 0

    # 🔹 Legal word trigger
    keyword_risk = 0
    legal_words = config.get("risk_triggers", {}).get("legal_words", [])

    for word in legal_words:
        if word.lower() in summary.lower():
            keyword_risk += 2

    risk_score += keyword_risk
    risk_contributors["keyword_risk"] = keyword_risk

    # 🔹 Escalation intent trigger
    intent_risk = 0
    escalation_keywords = config.get("risk_triggers", {}).get(
        "escalation_keywords", []
    )

    for intent in intents:
        if any(keyword in intent.lower() for keyword in escalation_keywords):
            intent_risk += 2

    risk_score += intent_risk
    risk_contributors["intent_risk"] = intent_risk

    # 🔹 Classify risk
    risk_level = classify_risk(risk_score)

    # 🔥 Compliance detection
    compliance_violations = detect_compliance_violations(summary, config)

    # 🔥 Outcome classification
    outcome = classify_outcome(ai_output, risk_level, config)

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "escalation_required": risk_level == "HIGH",
        "risk_contributors": risk_contributors,
        "compliance": {
            "violations": compliance_violations,
            "violation_count": len(compliance_violations)
        },
        "outcome": outcome
    }
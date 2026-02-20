from app.services.risk_scorer import classify_risk


def detect_compliance_violations(summary: str, config: dict):
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


def calculate_topic_drift(ai_output: dict, config: dict):

    primary_intent = ai_output.get("primary_intent", "")
    key_topics = [t.lower() for t in ai_output.get("key_topics", [])]

    topic_config = config.get("topic_control", {})

    allowed_intents = topic_config.get("allowed_intents", [])
    allowed_topics = [t.lower() for t in topic_config.get("allowed_topics", [])]
    drift_threshold = topic_config.get("drift_threshold", 0.5)

    # Intent mismatch
    intent_mismatch = 1 if primary_intent and primary_intent not in allowed_intents else 0

    # Topic mismatch ratio
    if not key_topics:
        topic_mismatch_ratio = 0
    else:
        unrelated_topics = [
            topic for topic in key_topics
            if topic not in allowed_topics
        ]
        topic_mismatch_ratio = len(unrelated_topics) / len(key_topics)

    # Final drift score
    drift_score = round((intent_mismatch + topic_mismatch_ratio) / 2, 2)

    return {
        "drift_score": drift_score,
        "intent_mismatch": bool(intent_mismatch),
        "topic_mismatch_ratio": round(topic_mismatch_ratio, 2),
        "threshold_exceeded": drift_score >= drift_threshold
    }


def classify_outcome(ai_output: dict, risk_level: str, config: dict):

    resolution_status = ai_output.get("resolution_status", "").upper()

    # Prefer AI resolution
    if resolution_status in ["RESOLVED", "ESCALATED", "PENDING"]:
        return {
            "type": resolution_status,
            "reason": "Derived from AI behavioral analysis"
        }

    # Fallback logic (optional)
    if risk_level == "HIGH":
        return {
            "type": "ESCALATED",
            "reason": "High risk detected"
        }

    return {
        "type": "COMPLETED",
        "reason": "No escalation detected"
    }


def run_rule_engine(ai_output: dict, config: dict):

    summary = ai_output.get("summary", "")
    primary_intent = ai_output.get("primary_intent", "").lower()

    risk_score = 0
    risk_contributors = {}

    # 🔹 AI Behavioral Risk (0–1 → 0–3 scale)
    ai_risk = ai_output.get("risk_score", 0)
    ai_risk_component = round(ai_risk * 3)

    risk_score += ai_risk_component
    risk_contributors["ai_behavioral_risk"] = ai_risk_component

    # 🔹 Legal keyword risk
    keyword_risk = 0
    legal_words = config.get("risk_triggers", {}).get("legal_words", [])

    for word in legal_words:
        if word.lower() in summary.lower():
            keyword_risk += 2

    risk_score += keyword_risk
    risk_contributors["keyword_risk"] = keyword_risk

    # 🔹 Intent escalation risk
    intent_risk = 0
    escalation_keywords = config.get("risk_triggers", {}).get("escalation_keywords", [])

    if any(keyword.lower() in primary_intent for keyword in escalation_keywords):
        intent_risk += 2

    risk_score += intent_risk
    risk_contributors["intent_risk"] = intent_risk

    # 🔹 Risk classification
    risk_level = classify_risk(risk_score)

    # 🔹 Compliance
    compliance_violations = detect_compliance_violations(summary, config)

    # 🔹 Topic Drift (percentage-based)
    topic_drift = calculate_topic_drift(ai_output, config)

    # 🔹 Outcome
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
        "topic_control": topic_drift,
        "outcome": outcome
    }
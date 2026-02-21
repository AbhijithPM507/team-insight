from app.services.risk_scorer import classify_risk


# ---------------------------------------------------------
# 🔹 Compliance Detection
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# 🔹 Topic Drift Analysis
# ---------------------------------------------------------

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

    drift_score = round((intent_mismatch + topic_mismatch_ratio) / 2, 2)

    return {
        "drift_score": drift_score,
        "intent_mismatch": bool(intent_mismatch),
        "topic_mismatch_ratio": round(topic_mismatch_ratio, 2),
        "threshold_exceeded": drift_score >= drift_threshold
    }


# ---------------------------------------------------------
# 🔹 Outcome Classification
# ---------------------------------------------------------

def classify_outcome(ai_output: dict, risk_level: str, config: dict):

    resolution_status = ai_output.get("resolution_status", "").upper()

    if resolution_status in ["RESOLVED", "ESCALATED", "PENDING"]:
        return {
            "type": resolution_status,
            "reason": "Derived from AI behavioral analysis"
        }

    if risk_level == "HIGH":
        return {
            "type": "ESCALATED",
            "reason": "High risk detected"
        }

    return {
        "type": "COMPLETED",
        "reason": "No escalation detected"
    }


# ---------------------------------------------------------
# 🔹 Main Rule Engine
# ---------------------------------------------------------

def run_rule_engine(ai_output: dict, config: dict):

    summary = ai_output.get("summary", "")
    primary_intent = ai_output.get("primary_intent", "").lower()
    ai_risk = ai_output.get("risk_score", 0)

    risk_score = 0
    risk_contributors = []

    weights = config.get("risk_weights", {})
    triggers = config.get("risk_triggers", {})

    # -------------------------------------------------
    # 🔹 1. AI Behavioral Risk (Configurable Weight)
    # -------------------------------------------------
    behavioral_weight = weights.get("ai_behavioral_multiplier", 3)
    ai_risk_component = round(ai_risk * behavioral_weight)

    risk_score += ai_risk_component
    risk_contributors.append({
        "factor": "ai_behavioral_risk",
        "impact": ai_risk_component
    })

    # -------------------------------------------------
    # 🔹 2. Keyword-Based Risk
    # -------------------------------------------------
    keyword_weight = weights.get("keyword_match", 2)
    keyword_risk = 0

    for category, keywords in triggers.items():
        if not isinstance(keywords, list):
            continue

        for word in keywords:
            if word.lower() in summary.lower():
                keyword_risk += keyword_weight
                risk_contributors.append({
                    "factor": f"{category}_keyword_match",
                    "impact": keyword_weight
                })

    risk_score += keyword_risk

    # -------------------------------------------------
    # 🔹 3. Intent-Based Escalation Risk
    # -------------------------------------------------
    intent_weight = weights.get("intent_match", 2)
    intent_risk = 0

    escalation_intents = triggers.get("escalation_intents", [])

    if any(keyword.lower() in primary_intent for keyword in escalation_intents):
        intent_risk += intent_weight
        risk_contributors.append({
            "factor": "intent_escalation_match",
            "impact": intent_weight
        })

    risk_score += intent_risk

    # -------------------------------------------------
    # 🔹 4. Escalation Threshold
    # -------------------------------------------------
    escalation_threshold = config.get("escalation_threshold", 6)

    risk_level = classify_risk(risk_score)

    escalation_required = risk_score >= escalation_threshold

    # -------------------------------------------------
    # 🔹 5. Compliance Check
    # -------------------------------------------------
    compliance_violations = detect_compliance_violations(summary, config)

    # -------------------------------------------------
    # 🔹 6. Topic Drift
    # -------------------------------------------------
    topic_drift = calculate_topic_drift(ai_output, config)

    # -------------------------------------------------
    # 🔹 7. Outcome
    # -------------------------------------------------
    outcome = classify_outcome(ai_output, risk_level, config)

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "escalation_required": escalation_required,
        "risk_contributors": risk_contributors,
        "compliance": {
            "violations": compliance_violations,
            "violation_count": len(compliance_violations)
        },
        "topic_control": topic_drift,
        "outcome": outcome
    }
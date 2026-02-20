from app.models.response_models import (
    AnalyzeResponse,
    EmotionSegment,
    RiskAnalysis,
)


def run_full_analysis(request):
    """
    Main orchestration function.
    Later this will:
    - Call AI extractor
    - Run rule engine
    - Calculate risk
    - Score agent
    """

    # ---- MOCK AI OUTPUT ----
    summary = "Customer called regarding a refund issue for a credit card transaction."
    language = "English"
    sentiment = "Negative"

    timeline = [
        EmotionSegment(time="00:00-01:30", emotion="Neutral"),
        EmotionSegment(time="01:30-03:10", emotion="Frustrated"),
        EmotionSegment(time="03:10-05:00", emotion="Angry"),
    ]

    intents = ["Refund request"]
    entities = ["Credit Card", "Transaction ID"]

    # ---- MOCK RISK ENGINE ----
    risk = RiskAnalysis(
        compliance_risk_score=72,
        escalation_probability=0.64,
        churn_risk=0.58,
    )

    call_outcome = "Escalation Likely"
    agent_score = 81
    policy_flags = ["FINANCIAL_DISPUTE_RISK"]

    return AnalyzeResponse(
        conversation_summary=summary,
        language_detected=language,
        sentiment_overall=sentiment,
        timeline_emotion_analysis=timeline,
        primary_intents=intents,
        key_entities=entities,
        risk_analysis=risk,
        call_outcome_prediction=call_outcome,
        agent_performance_score=agent_score,
        policy_flags=policy_flags,
    )
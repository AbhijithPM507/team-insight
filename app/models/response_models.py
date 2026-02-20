from pydantic import BaseModel
from typing import List


class EmotionSegment(BaseModel):
    time: str
    emotion: str


class RiskAnalysis(BaseModel):
    compliance_risk_score: int
    escalation_probability: float
    churn_risk: float


class AnalyzeResponse(BaseModel):
    conversation_summary: str
    language_detected: str
    sentiment_overall: str
    timeline_emotion_analysis: List[EmotionSegment]
    primary_intents: List[str]
    key_entities: List[str]
    risk_analysis: RiskAnalysis
    call_outcome_prediction: str
    agent_performance_score: int
    policy_flags: List[str]
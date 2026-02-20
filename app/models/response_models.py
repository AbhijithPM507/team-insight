from pydantic import BaseModel, Field
from typing import List


class EmotionSegment(BaseModel):
    time: str
    emotion: str
    confidence: float | None = None


class RiskContributor(BaseModel):
    factor: str
    impact: int


class RiskAnalysis(BaseModel):
    compliance_risk_score: int
    escalation_probability: float
    churn_risk: float
    risk_contributors: List[RiskContributor]


class AnalyzeResponse(BaseModel):
    conversation_summary: str
    languages_detected: List[str]
    sentiment_overall: str
    timeline_emotion_analysis: List[EmotionSegment]
    primary_intents: List[str]
    key_entities: List[str]
    risk_analysis: RiskAnalysis
    call_outcome_prediction: str
    agent_performance_score: int
    policy_flags: List[str]
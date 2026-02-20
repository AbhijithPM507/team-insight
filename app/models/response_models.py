from pydantic import BaseModel, Field
from typing import List, Optional


class EmotionSegment(BaseModel):
    time: str = Field(description="Time range of the segment")
    emotion: str = Field(description="Detected emotion in this segment")
    confidence: Optional[float] = Field(
        default=None,
        description="Confidence score for emotion classification (0-1)"
    )


class RiskContributor(BaseModel):
    factor: str = Field(description="Reason contributing to risk score")
    impact: int = Field(description="Impact weight added to risk score")


class RiskAnalysis(BaseModel):
    compliance_risk_score: int = Field(
        description="Overall compliance risk score (0-100)"
    )
    escalation_probability: float = Field(
        description="Probability of escalation (0-1)"
    )
    churn_risk: float = Field(
        description="Probability of customer churn (0-1)"
    )
    risk_contributors: List[RiskContributor] = Field(
        description="List of factors contributing to risk score"
    )


class DomainAnalysis(BaseModel):
    detected_domain: Optional[str] = Field(
        default=None,
        description="Detected business domain (banking, telecom, etc.)"
    )
    domain_confidence: Optional[float] = Field(
        default=None,
        description="Confidence score of detected domain"
    )


class AnalyzeResponse(BaseModel):
    conversation_summary: str
    languages_detected: List[str]
    sentiment_overall: str
    timeline_emotion_analysis: List[EmotionSegment]
    primary_intents: List[str]
    key_entities: List[str]

    domain_analysis: Optional[DomainAnalysis] = None

    risk_analysis: RiskAnalysis

    call_outcome_prediction: str
    agent_performance_score: int

    policy_flags: List[str]
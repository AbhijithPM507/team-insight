# InsightX – Multimodal Conversation Intelligence API

## Overview

InsightX is a backend-only, API-first conversation intelligence engine designed to analyze multimodal customer conversations (text or voice) and generate structured enterprise insights.

The system combines:
- Multimodal AI processing (Gemini + ElevenLabs)
- Deterministic domain rule enforcement
- Quantitative risk modeling
- Compliance and behavioral intelligence

The API is implemented using FastAPI and follows OpenAPI 3.1 standards.

---

##  Base URL

Local development:
http://127.0.0.1:8000


Swagger UI:
http://127.0.0.1:8000/docs



OpenAPI JSON:
http://127.0.0.1:8000/openapi.json


---

##  Endpoint

### POST `/analyze`

Analyzes a conversation (text or audio) and returns structured enterprise intelligence.

---

## Request Format

### Content Type:
multipart/form-data


---

##  Request Parameters

| Field | Type | Required | Description |
|--------|------|----------|------------|
| transcript | string | Optional* | Text-based conversation transcript |
| audio_file | file (.wav, .mp3) | Optional* | Audio recording |
| client_config | string (JSON) | Optional | Domain configuration & rule customization |

\* Either `transcript` OR `audio_file` must be provided.

---

Request (Audio/Text + Config)
        ↓
Language Detection
        ↓
AI Insight Extraction (Gemini)
        ↓
Domain Rule Engine
        ↓
Advanced Risk & Compliance Analysis
        ↓
Structured Enterprise JSON Response

## Success Response (JSON)
{
  "analysis": {
    "conversation_summary": "Customer reports unauthorized transaction and requests resolution.",
    "detected_domain": "banking",
    "primary_intent": "REPORT_FRAUD",
    "ai_risk_score": 0.82,
    "key_topics": ["Credit Card", "Unauthorized Transaction"],
    "agent_analysis": {
      "tone": "Professional",
      "empathy_level": 0.85,
      "protocol_adherence": true
    },
    "customer_analysis": {
      "tone": "Frustrated",
      "satisfaction_score": 4
    },
    "resolution_status": "ESCALATED",
    "language": "English",
    "overall_sentiment": "Angry"
  },
  "risk_assessment": {
    "rule_based_risk_score": 75,
    "risk_level": "HIGH",
    "escalation_required": true,
    "risk_contributors": [
      {
        "factor": "Unauthorized keyword detected",
        "impact": 30
      }
    ]
  },
  "compliance": {
    "violations": ["Agent failed to verify identity"],
    "pii_detected": ["Partial credit card number"],
    "rule_based_flags": ["FINANCIAL_DISPUTE"]
  },
  "topic_control": {
    "sensitive_topics_detected": true,
    "restricted_terms": []
  },
  "outcome": {
    "resolution_status": "ESCALATED",
    "rule_based_override": null
  },
  "domain_used_for_rules": "banking"
}

## Error Responses

400 - Bad Request
{
  "detail": "Either transcript or audio_file must be provided."
}

500 - Internal Server Error
{
  "detail": "Internal processing error"
}

## Performance Considerations

- Audio processing latency depends on file duration and external transcription API response time.
- AI inference time depends on Gemini model response latency.
- The system is designed for backend integration into enterprise workflows.
- Current implementation prioritizes modularity and clarity over horizontal scaling.
- Production deployment would include caching, async processing, and rate limiting.
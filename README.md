
# InsightX – Context-Aware Multimodal Conversation Intelligence API

## 🚀 Overview

InsightX is an enterprise-ready backend API designed to analyze multimodal customer conversations (voice or text) and generate structured intelligence including:

- Conversation summaries
- Sentiment analysis
- Intent detection
- Entity extraction
- Domain detection
- Compliance risk scoring
- Escalation probability
- Churn risk estimation
- Agent performance scoring

The system is configurable per business domain and built for integration into banking, telecom, insurance, and customer support environments.

---

## 🏗 Architecture

```text
Client Application
        │
        ▼
FastAPI Backend
        │
        ▼
Multimodal AI Layer (Gemini + ElevenLabs)
        │
        ▼
Domain Rule Engine
        │
        ▼
Risk & Impact Engine
        │
        ▼
Structured Enterprise JSON Output


### Key Modules

| File | Responsibility |
|------|---------------|
| routes.py | API layer |
| ai_service.py | Multimodal AI processing |
| rule_engine.py | Domain-based logic |
| risk_engine.py | Quantitative scoring |
| analysis_service.py | Orchestration |
| response_models.py | Structured output schema |

---

## 🤖 AI Usage Approach

### Audio Processing
- ElevenLabs Scribe v2
- Speaker diarization enabled

### Language Model
- Gemini 2.5 Flash
- Structured JSON extraction
- Domain classification
- Behavioral analysis

### AI Output Includes

- detected_domain
- summary
- primary_intent
- risk_score
- agent_analysis
- customer_analysis
- resolution_status
- key_topics
- language

AI output is post-processed by deterministic rule logic to ensure explainability.

---

### Request Format

The API expects `multipart/form-data`.

Fields:
- transcript (optional)
- audio_file (optional)
- client_config (JSON string, optional)

Either transcript or audio_file must be provided.
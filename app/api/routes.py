from fastapi import APIRouter, HTTPException
from app.models.request_models import AnalyzeRequest
from app.services.analysis_service import run_full_analysis

router = APIRouter()


@router.post("/analyze")
def analyze(request: AnalyzeRequest):
    """
    Main analysis endpoint.
    """

    # 🔹 Validate domain
    if not request.client_config or "domain" not in request.client_config:
        raise HTTPException(
            status_code=400,
            detail="Domain must be provided inside client_config"
        )

    domain = request.client_config.get("domain")

    # 🔹 Use transcript for now (Dev 2 AI not integrated yet)
    if request.transcript:
        conversation_text = request.transcript
    else:
        conversation_text = "Audio input received"

    # 🔥 TEMPORARY AI OUTPUT (Replace when Dev 2 connects)
    ai_output = {
        "summary": conversation_text,
        "sentiment": "very_negative",
        "intents": ["cancel connection"]
    }

    try:
        return run_full_analysis(ai_output, domain)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal processing error")
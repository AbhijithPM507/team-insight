from fastapi import APIRouter, HTTPException
from app.models.request_models import AnalyzeRequest
from app.models.response_models import AnalyzeResponse
from app.services.analysis_service import run_full_analysis
from app.services.webhook_service import send_to_n8n

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):

    try:
        result = run_full_analysis(request)

        # Optional orchestration trigger
        if request.client_config.get("enable_workflow", False):
            send_to_n8n(result.dict())

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
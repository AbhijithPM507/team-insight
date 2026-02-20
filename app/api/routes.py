from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import json

from app.services.analysis_service import run_full_analysis
from app.services.ai_service import run_ai_layer  # Dev 2 will implement this

router = APIRouter()


@router.post("/analyze")
async def analyze(
    transcript: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    client_config: Optional[str] = Form(None)
):
    """
    Accepts:
    - transcript (text)
    - audio_file (uploaded file)
    - client_config (JSON string)
    """

    if not transcript and not audio_file:
        raise HTTPException(
            status_code=400,
            detail="Either transcript or audio_file must be provided."
        )

    try:
        parsed_config = json.loads(client_config) if client_config else {}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid client_config JSON")

    # 🔹 Read audio if provided
    audio_bytes = None
    if audio_file:
        audio_bytes = await audio_file.read()

    try:
        # 🔹 Call Dev 2 AI Layer
        ai_output = await run_ai_layer(
            transcript=transcript,
            audio_bytes=audio_bytes,
            client_config=parsed_config
        )

        # 🔹 Domain resolution
        client_domain = parsed_config.get("domain")
        detected_domain = ai_output.get("detected_domain")

        if client_domain:
            final_domain = client_domain
        elif detected_domain:
            final_domain = detected_domain
        else:
            final_domain = "general"

        # 🔹 Call Dev 3 + Dev 4 integration layer
        return run_full_analysis(ai_output, final_domain)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
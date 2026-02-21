from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import json
import logging

from app.services.analysis_service import run_full_analysis
from app.services.ai_service import run_ai_layer  # Dev 2 will implement this

router = APIRouter()
logger = logging.getLogger("routes")


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

    logger.info("Received /analyze request")

    if not transcript and not audio_file:
        logger.warning("Neither transcript nor audio_file provided")
        raise HTTPException(
            status_code=400,
            detail="Either transcript or audio_file must be provided."
        )

    # 🔹 Parse client config
    try:
        parsed_config = json.loads(client_config) if client_config else {}
        logger.info("client_config parsed successfully")
    except Exception:
        logger.error("Invalid client_config JSON")
        raise HTTPException(status_code=400, detail="Invalid client_config JSON")

    # 🔹 Read audio if provided
    audio_bytes = None
    if audio_file:
        logger.info(f"Audio file received: {audio_file.filename}")
        audio_bytes = await audio_file.read()
        logger.info(f"Audio file size: {len(audio_bytes)} bytes")

    try:
        # 🔹 Call Dev 2 AI Layer
        logger.info("Calling AI layer...")
        ai_output = await run_ai_layer(
            transcript=transcript,
            audio_bytes=audio_bytes,
            client_config=parsed_config
        )
        logger.info("AI layer completed successfully")

        # 🔹 Domain resolution
        client_domain = parsed_config.get("domain")
        detected_domain = ai_output.get("detected_domain")

        if client_domain:
            final_domain = client_domain
            logger.info(f"Using client-provided domain: {final_domain}")
        elif detected_domain:
            final_domain = detected_domain
            logger.info(f"Using AI-detected domain: {final_domain}")
        else:
            final_domain = "general"
            logger.info("No domain provided. Defaulting to 'general'")

        # 🔹 Call Dev 3 + Dev 4 integration layer
        logger.info("Running full analysis layer...")
        result = run_full_analysis(ai_output, final_domain)

        logger.info("Analysis completed successfully")
        return result

    except ValueError as e:
        logger.warning(f"ValueError during processing: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.exception("Unexpected error during /analyze")
        raise HTTPException(status_code=500, detail=str(e))
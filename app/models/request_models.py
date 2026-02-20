from pydantic import BaseModel, model_validator
from typing import Optional, Dict, Any


class AnalyzeRequest(BaseModel):
    transcript: Optional[str] = None
    audio_base64: Optional[str] = None
    client_config: Dict[str, Any]

    @model_validator(mode="after")
    def validate_input(self):
        if not self.transcript and not self.audio_base64:
            raise ValueError("Either transcript or audio_base64 must be provided.")
        return self
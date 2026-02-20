from pydantic import BaseModel, Field, model_validator
from typing import Optional, Dict, Any


class AnalyzeRequest(BaseModel):
    transcript: Optional[str] = Field(
        default=None,
        description="Text-based customer conversation transcript"
    )

    audio_base64: Optional[str] = Field(
        default=None,
        description="Base64 encoded audio file"
    )

    client_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Client configuration influencing analysis"
    )

    @model_validator(mode="after")
    def validate_input(self):
        if not self.transcript and not self.audio_base64:
            raise ValueError("Either transcript or audio_base64 must be provided.")
        return self
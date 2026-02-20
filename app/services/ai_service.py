import os
import json
import tempfile
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from google import genai

load_dotenv()

GEMINI_MODEL = "gemini-2.5-flash"
SCRIBE_MODEL = "scribe_v2"


async def run_ai_layer(transcript=None, audio_bytes=None, client_config=None) -> dict:
    """
    Main AI entry point for Dev 2 layer.
    Accepts transcript OR audio bytes.
    Returns structured Python dict for Dev 3.
    """

    if not transcript and not audio_bytes:
        raise ValueError("Either transcript or audio must be provided.")

    # 🔹 Initialize clients ONLY when needed
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    eleven_api_key = os.getenv("ELEVENLABS_API_KEY")

    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not configured.")
    if not eleven_api_key:
        raise ValueError("ELEVENLABS_API_KEY not configured.")

    gemini_client = genai.Client(api_key=gemini_api_key)
    el_client = ElevenLabs(api_key=eleven_api_key)

    # 🔹 If audio → transcribe first
    if audio_bytes:
        transcript = await _transcribe_audio(audio_bytes, el_client)

    # 🔹 Generate insights
    raw_output = _generate_insights(transcript, gemini_client)

    # 🔹 Clean & parse JSON safely
    try:
        clean_json = (
            raw_output.strip()
            .replace("```json", "")
            .replace("```", "")
        )
        return json.loads(clean_json)

    except Exception:
        raise ValueError("AI returned invalid JSON format.")


# -------------------------------------------------------------------
# 🔹 Private Helper: Audio Transcription
# -------------------------------------------------------------------

async def _transcribe_audio(audio_bytes: bytes, el_client: ElevenLabs) -> str:
    """
    Sends audio bytes to ElevenLabs Scribe.
    Returns labeled transcript string.
    """

    # Write temporary file (ElevenLabs expects file object)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_bytes)
        temp_path = temp_audio.name

    with open(temp_path, "rb") as audio_file:
        response = el_client.speech_to_text.convert(
            file=audio_file,
            model_id=SCRIBE_MODEL,
            tag_audio_events=True,
            diarize=True
        )

    os.remove(temp_path)

    # Build speaker-labeled transcript
    lines = []
    current_speaker = None
    current_line = ""

    for word in response.words:
        if word.speaker_id != current_speaker:
            if current_line:
                lines.append(f"Speaker {current_speaker}: {current_line.strip()}")
            current_speaker = word.speaker_id
            current_line = word.text
        else:
            current_line += f" {word.text}"

    if current_line:
        lines.append(f"Speaker {current_speaker}: {current_line.strip()}")

    return "\n".join(lines)


# -------------------------------------------------------------------
# 🔹 Private Helper: Gemini Intelligence
# -------------------------------------------------------------------

def _generate_insights(transcript: str, gemini_client) -> str:
    """
    Sends transcript to Gemini.
    Returns raw JSON string.
    """

    prompt = f"""
    You are an Enterprise Conversation Intelligence engine.

    Transcript:
    {transcript}

     YOUR MISSION:
        Analyze the behavior and technical content of this call. Return a JSON object with:
        1. 'detected_domain': (banking, telecom, insurance, healthcare, general).
        2. 'summary': 2-sentence English summary.
        3. 'primary_intent': Standardized English slug (e.g., "CLOSE_CONNECTION", "REPORT_FRAUD").
        4. 'risk_score': (0.0 to 1.0) based on data sensitivity and urgency.
        5. 'agent_analysis': {{"tone": "Professional/Rude/Passive", "empathy_level": 0.0-1.0, "protocol_adherence": true/false}}
        6. 'customer_analysis': {{"tone": "Frustrated/Calm/Panic", "satisfaction_score": 1-10}}
        7. 'resolution_status': "RESOLVED", "ESCALATED", or "PENDING".
        8. 'key_topics': List of English tags.
        9. 'language': Detected language of the transcript.

        OUTPUT: Return ONLY the JSON object. All text values MUST be in ENGLISH.
    """

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return response.text
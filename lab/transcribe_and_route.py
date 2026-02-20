import os
import json
import re
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from google import genai 

load_dotenv()

# Client Initialization
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
GEMINI_MODEL = "gemini-2.5-flash" 

class ElevenLabsInsightEngine:
    def __init__(self):
        el_api_key = os.getenv("ELEVENLABS_API_KEY")
        if not el_api_key:
             raise ValueError("❌ ELEVENLABS_API_KEY not found in .env file!")
        self.el_client = ElevenLabs(api_key=el_api_key)
        self.model_id = "scribe_v2"

    def _clean_text(self, text):
        """Internal helper to scrub direct text input of junk."""
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = " ".join(text.split())         # Normalize whitespace
        return text

    def get_transcript(self, audio_file_path: str):
        print(f"📡 Sending to ElevenLabs Scribe v2...")
        with open(audio_file_path, "rb") as audio_file:
            response = self.el_client.speech_to_text.convert(
                file=audio_file,
                model_id=self.model_id,
                tag_audio_events=True, 
                diarize=True
            )
        text = response.text or ""
        events = [w.text for w in response.words if w.type == "audio_event"]
        return text, events, response

    def get_labeled_transcript(self, raw_data):
        lines = []
        current_speaker = None
        current_line = ""
        for word in raw_data.words:
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
    
    def get_english_insights(self, labeled_transcript, audio_events):
        prompt = f"""
        Analyze this conversation. Return a JSON object with:
        1. 'detected_domain': (banking, telecom, insurance, healthcare, general).
        2. 'summary': 2-sentence English summary.
        3. 'primary_intent': Standardized English slug (e.g., "CLOSE_CONNECTION", "REPORT_FRAUD").
        4. 'risk_score': (0.0 to 1.0) based on data sensitivity and urgency.
        5. 'agent_analysis': {{"tone": "Professional/Rude/Passive", "empathy_level": 0.0-1.0}}
        6. 'customer_analysis': {{"tone": "Frustrated/Calm/Panic", "satisfaction_score": 1-10}}
        7. 'resolution_status': "RESOLVED", "ESCALATED", or "PENDING".
        8. 'key_topics': List of English tags.
        9. 'language': Detected language of original transcript.

        OUTPUT: Return ONLY the JSON object. All text values MUST be in ENGLISH.
        """
        print(f"🧠 Generating Deep Insights...")
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt, f"TRANSCRIPT: {labeled_transcript}", f"EVENTS: {audio_events}"]
        )
        return response.text

    def process_request(self, audio_path=None, direct_text=None):
        """Unified entry point for Audio or Text."""
        final_labeled_text = ""
        audio_events = []

        if audio_path and os.path.exists(audio_path):
            text, audio_events, raw_data = self.get_transcript(audio_path)
            final_labeled_text = self.get_labeled_transcript(raw_data)
        elif direct_text:
            print("📝 Direct text input detected.")
            final_labeled_text = self._clean_text(direct_text)
        else:
            return {"status": "error", "message": "No valid input provided."}

        json_string = self.get_english_insights(final_labeled_text, audio_events)
        
        try:
            clean_json = json_string.strip().replace('```json', '').replace('```', '')
            return json.loads(clean_json)
        except Exception as e:
            return {"status": "error", "message": str(e), "raw": json_string}

# --- EXECUTION ---
if __name__ == "__main__":
    engine = ElevenLabsInsightEngine()

    # Test Mode: Toggle as needed
    result = engine.process_request(audio_path="lab/samples/call1.mp4")
    #result = engine.process_request(direct_text="Speaker 0: Hello. Speaker 1: Stop recording please.")

    print(json.dumps(result, indent=4, ensure_ascii=False))
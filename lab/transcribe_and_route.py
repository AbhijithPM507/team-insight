import os
import json
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from google import genai  # Modern 2026 SDK

# 1. Load environment variables BEFORE doing anything else
load_dotenv()

# 2. Get the API Key and verify it's not None
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file!")

# 3. Initialize the Client (No more genai.configure needed)
# Note: 'genai' here refers to the 'google.genai' package you imported
client = genai.Client(api_key=api_key)
GEMINI_MODEL = "gemini-2.5-flash" 

class ElevenLabsInsightEngine:
    def __init__(self):
        el_api_key = os.getenv("ELEVENLABS_API_KEY")
        if not el_api_key:
             raise ValueError("❌ ELEVENLABS_API_KEY not found in .env file!")
        self.el_client = ElevenLabs(api_key=el_api_key)
        self.model_id = "scribe_v2"

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
        """Phase 3: Deep Behavioral Analysis for Dev 3 Integration."""
        prompt = f"""
        You are an expert Enterprise Conversation Intelligence agent.
        
        INPUT DATA:
        Transcript (Multilingual): {labeled_transcript}
        Audio Events: {audio_events}
        
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
        
        print(f"🧠 Generating Deep Insights for Dev 3...")
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        return response.text

# --- EXECUTION ---
if __name__ == "__main__":
    engine = ElevenLabsInsightEngine()
    # Double-check the path to your file
    audio_path = "lab/samples/call1.mp4" 
    
    if os.path.exists(audio_path):
        text, events, raw_data = engine.get_transcript(audio_path)
        labeled_transcript = engine.get_labeled_transcript(raw_data)
        
        print(f"\n📢 Labeled Transcript:\n{labeled_transcript}")

        json_string = engine.get_english_insights(labeled_transcript, events)

        try:
            # Clean up potential markdown from the LLM
            clean_json = json_string.strip().replace('```json', '').replace('```', '')
            final_output = json.loads(clean_json)
            print("\n🔥 FINAL ENTERPRISE JSON (English):")
            print(json.dumps(final_output, indent=4, ensure_ascii=False))
        except Exception as e:
            print(f"❌ JSON Parsing Error: {e}")
            print(f"Raw Output from Gemini: {json_string}")
    else:
        print(f"❌ Audio file not found at {audio_path}")
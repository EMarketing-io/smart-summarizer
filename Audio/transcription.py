import openai
from Audio.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def transcribe_audio(audio_path):
    print("🎙️ Transcribing with OpenAI Whisper API...")
    with open(audio_path, "rb") as audio_file:
        response = openai.Audio.transcribe(
            model="whisper-1", file=audio_file, response_format="text", task="translate"
        )
        return response.strip()

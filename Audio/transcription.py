import openai
from pydub import AudioSegment
from audio.config import OPENAI_API_KEY

# 🔐 Set the OpenAI API key loaded from the .env configuration
openai.api_key = OPENAI_API_KEY


# 🎧 Transcribe an audio file to English text using OpenAI Whisper API
def transcribe_audio(audio_path):
    print("🎙️ Transcribing with OpenAI Whisper API...")

    # 📂 Open the audio file in binary read mode
    with open(audio_path, "rb") as audio_file:
        # 📡 Send the audio to OpenAI Whisper for transcription
        response = openai.Audio.transcribe(
            model="whisper-1",         # Whisper model for audio-to-text
            file=audio_file,           # Audio file stream
            response_format="text",    # Return plain text response
            task="translate"           # Auto-translates non-English to English
        )

        # 🧾 Return the transcribed text, stripped of extra whitespace
        return response.strip()

def split_audio(audio_path, chunk_length_ms=15 * 60 * 1000):
    audio = AudioSegment.from_file(audio_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i : i + chunk_length_ms]
        chunk_path = f"{audio_path}_part{i // chunk_length_ms}.mp3"
        chunk.export(chunk_path, format="mp3")
        chunks.append(chunk_path)
    return chunks
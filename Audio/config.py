import os
from dotenv import load_dotenv

# 🔐 Load environment variables from the .env file into the runtime environment
load_dotenv()

# 🧠 OpenAI API Key used for accessing GPT-4 and Whisper models
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 📁 Google Drive folder ID where audio-based summaries (meeting notes) will be uploaded
AUDIO_DRIVE_FOLDER_ID = os.getenv("AUDIO_DRIVE_FOLDER_ID")

# 📦 Standard Libraries
import os
import io
import tempfile
import requests

# 🌐 Google API Libraries
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.oauth2 import service_account

# 🔐 Environment variable loader
from dotenv import load_dotenv

load_dotenv()

# 🔧 Config from .env
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
AUDIO_DRIVE_FOLDER_ID = os.getenv(
    "AUDIO_DRIVE_FOLDER_ID"
)  # Replace with your actual .env key
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


# 🔐 Authenticate using service account
def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=credentials)


# ⬇️ Download an audio file from Google Drive to a temp file
def download_audio_from_drive(file_id):
    print("🌐 Downloading shared file using public link fallback...")

    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(url, stream=True)

    if response.status_code != 200:
        raise Exception(
            f"❌ Failed to download file: {response.status_code} - {response.text}"
        )

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".m4a")
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            temp_file.write(chunk)

    temp_file.close()
    print(f"✅ Downloaded file to: {temp_file.name}")
    return temp_file.name


# 📤 Uploads a DOCX file (in memory) to a Shared Drive
def upload_file_to_drive_in_memory(
    file_data, folder_id=AUDIO_DRIVE_FOLDER_ID, final_name="Meeting Notes.docx"
):
    service = get_drive_service()

    file_metadata = {
        "name": final_name,
        "parents": [folder_id],
        "mimeType": "application/vnd.google-apps.document",
    }

    file_stream = io.BytesIO(file_data)
    media = MediaIoBaseUpload(
        file_stream,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=True,
    )

    file = (
        service.files()
        .create(
            body=file_metadata,
            media_body=media,
            fields="id",
            supportsAllDrives=True,  # ✅ Needed for Shared Drive upload
        )
        .execute()
    )

    print(f"📤 File uploaded: {file.get('id')}")
    return file.get("id")

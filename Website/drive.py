import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from dotenv import load_dotenv

# 🔐 Load environment variables from .env
load_dotenv()

# 📁 Config values loaded from environment
FOLDER_ID = os.getenv("WEBSITE_DRIVE_FOLDER_ID")  # Shared Drive folder ID
SERVICE_ACCOUNT_FILE = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_FILE"
)  # Service account JSON path
SCOPES = ["https://www.googleapis.com/auth/drive.file"]  # Required Drive scope


# 🔐 Auth using service account for headless Drive access (Shared Drives supported)
def authenticate_google_drive():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=credentials)


# 📤 Uploads a DOCX file (from memory) to Google Drive as a Google Doc in a Shared Drive
def upload_docx_to_gdrive(docx_stream, filename):
    service = authenticate_google_drive()

    file_metadata = {
        "name": filename,
        "parents": [FOLDER_ID],
        "mimeType": "application/vnd.google-apps.document",
    }

    docx_stream.seek(0)
    docx_content = docx_stream.read()

    media = MediaInMemoryUpload(
        docx_content,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=True,
    )

    uploaded = (
        service.files()
        .create(
            body=file_metadata,
            media_body=media,
            fields="id, name",
            supportsAllDrives=True,  # ✅ Required for Shared Drives
        )
        .execute()
    )

    print(f"Uploaded to Google Drive as: {uploaded['name']} (ID: {uploaded['id']})")
    return uploaded["id"]


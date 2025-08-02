import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# 🔐 Load environment variables from .env
load_dotenv()

# 📁 Config values loaded from environment
FOLDER_ID = os.getenv("WEBSITE_DRIVE_FOLDER_ID")  # Google Drive folder ID for website summaries
GOOGLE_OAUTH_FILE = os.getenv("GOOGLE_OAUTH_FILE")  # Path to OAuth client secrets
TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH")  # Path to cached token
SCOPES = ["https://www.googleapis.com/auth/drive.file"]  # Minimum required Drive scope


# 🔐 Handles OAuth authentication and returns a Google Drive API service client
def authenticate_google_drive():
    creds = None

    # ✅ Load token from disk if available
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    # 🔁 If token is invalid or missing, refresh or start login flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        # Launch interactive login to fetch new token
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_OAUTH_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # 💾 Save token for reuse
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)

    # 📡 Return authorized Drive API client
    return build("drive", "v3", credentials=creds)


# 📤 Uploads a DOCX file (from memory) to Google Drive as a Google Doc
def upload_docx_to_gdrive(docx_stream, filename):

    # Ensure authenticated Drive API client
    service = authenticate_google_drive()

    # 📄 Metadata for the file being uploaded
    file_metadata = {
        "name": filename,
        "parents": [FOLDER_ID],
        "mimeType": "application/vnd.google-apps.document",  # Converts to Google Docs format
    }

    # Reset stream to beginning and read its content
    docx_stream.seek(0)
    docx_content = docx_stream.read()

    # 🗃️ Upload content using correct MIME type for Word files
    media = MediaInMemoryUpload(
        docx_content,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=True,
    )

    # 🚀 Upload to Google Drive and print result
    uploaded = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id, name")
        .execute()
    )

    print(f"Uploaded to Google Drive as: {uploaded['name']} (ID: {uploaded['id']})")
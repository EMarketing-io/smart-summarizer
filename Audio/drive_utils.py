# 📦 Standard Libraries
import os
import pickle
import io
import tempfile

# 🌐 Google API Libraries
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# 🔐 Environment variable loader
from dotenv import load_dotenv

# Load all variables from the .env file
load_dotenv()

# 🔧 Configuration from environment
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")  # Path to client_secrets.json
TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH")              # Path to save/restore user token


# 🔐 Authenticate with OAuth2 and return a Google Drive API client
def authenticate_with_oauth():
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    creds = None

    # ✅ Try to load cached credentials
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    # 🔄 Refresh expired token or start new OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        # Start browser login flow 
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

         # 💾 Save the refreshed/new token to disk
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)

    # ✅ Return authenticated Google Drive client
    return build("drive", "v3", credentials=creds)


# 🔁 Build Google Drive service — using API key or OAuth2 flow
def get_drive_service(api_key=None):
    if api_key:
        print("🔐 Using API Key authentication")
        return build("drive", "v3", developerKey=api_key)
    
    else:
        print("🔐 Using OAuth authentication")
        return authenticate_with_oauth()


# ⬇️ Download an audio file from Google Drive and store it temporarily
def download_audio_from_drive(file_id, api_key=None):
    service = get_drive_service(api_key)
    request = service.files().get_media(fileId=file_id)
    
    # Create a temp .mp3 file for the download
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

    # Stream the file from Drive
    downloader = MediaIoBaseDownload(temp_file, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Downloading audio: {int(status.progress() * 100)}%")

    temp_file.close()
    return temp_file.name


# 📤 Upload a DOCX file (in memory) to a target Google Drive folder
def upload_file_to_drive_in_memory(file_data, folder_id, api_key=None, final_name="Zoom Call Notes.docx"):
    service = get_drive_service(api_key)
    
    # 📝 Metadata for the new Drive file
    file_metadata = {"name": final_name, "parents": [folder_id]}

    # Convert byte content into an uploadable stream
    file_stream = io.BytesIO(file_data)
    media = MediaIoBaseUpload(
        file_stream,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=True,
    )

    # 🚀 Upload the file to Drive
    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )

    print(f"📤 File uploaded: {file.get('id')}")
    return file.get("id")
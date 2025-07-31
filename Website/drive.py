import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")
CLIENT_SECRETS_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_google_drive():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

def upload_docx_to_gdrive(docx_stream, filename):
    service = authenticate_google_drive()

    file_metadata = {
        'name': filename,
        'parents': [FOLDER_ID],
        'mimeType': 'application/vnd.google-apps.document'
    }

    docx_stream.seek(0)
    docx_content = docx_stream.read()

    media = MediaInMemoryUpload(docx_content, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document', resumable=True)

    uploaded = service.files().create(body=file_metadata, media_body=media, fields='id, name').execute()
    print(f"Uploaded to Google Drive as: {uploaded['name']} (ID: {uploaded['id']})")

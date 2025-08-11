# 📦 Standard Libraries
import os
import re
from dotenv import load_dotenv

# 🌐 Website Processing Modules
from website.extract import extract_text_from_url
from website.summarize import summarize_with_openai
from website.document import create_docx_in_memory as create_website_doc
from website.drive import upload_docx_to_gdrive

# 🎧 Audio Processing Modules
from audio.transcription import transcribe_audio, split_audio
from audio.summarizer import generate_summary
from audio.doc_generator import generate_docx as create_audio_doc
from audio.drive_utils import upload_file_to_drive_in_memory, download_audio_from_drive

# 📊 Google Sheets & Drive API
from googleapiclient.discovery import build
from google.oauth2 import service_account

# 🔐 Load environment variables
load_dotenv()
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
AUDIO_DRIVE_FOLDER_ID = os.getenv("AUDIO_DRIVE_FOLDER_ID")


# 🔗 Extract folder ID from Google Drive folder link
def extract_folder_id(drive_link):
    match = re.search(r"/folders/([a-zA-Z0-9_-]+)", drive_link)
    return match.group(1) if match else None


# 🔍 Get first .m4a file ID from folder
def get_first_m4a_file_id_in_folder(folder_id):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=credentials)

    results = (
        service.files()
        .list(
            q=f"'{folder_id}' in parents and mimeType contains 'audio' and trashed = false",
            pageSize=10,
            fields="files(id, name)",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
        )
        .execute()
    )

    files = results.get("files", [])
    for file in files:
        if file["name"].lower().endswith(".m4a"):
            print(f"🎯 Found audio file: {file['name']}")
            return file["id"]
    print("⚠️ No .m4a file found in folder.")
    return None


# 📁 Get folder name (used as company name)
def get_drive_folder_name(folder_id):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=credentials)

    folder = (
        service.files()
        .get(
            fileId=folder_id,
            fields="name",
            supportsAllDrives=True,
        )
        .execute()
    )

    return folder.get("name", "Company")


# 🌐 Extracts company name from URL
def format_website_name(url):
    domain = re.sub(r"https?://(www\\.)?", "", url).split("/")[0]
    parts = domain.split(".")
    ignore = {"com", "in", "net", "org", "www"}
    main_parts = [part for part in parts if part.lower() not in ignore]
    return main_parts[0].capitalize() if main_parts else "Website"


# 🚀 Main batch processor
def main():
    print("🚀 Smart Summariser - Website + Audio Mode")

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    service = build("sheets", "v4", credentials=credentials)

    # Load sheet rows
    sheet = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=GOOGLE_SHEET_ID, range="Sheet1!A2:F")
        .execute()
    )
    rows = sheet.get("values", [])
    if not rows:
        print("❌ No rows to process.")
        return

    for i, row in enumerate(rows, start=2):  # Starting from row 2
        date = row[0] if len(row) > 0 else ""
        website_url = row[1] if len(row) > 1 else ""
        audio_folder_link = row[2] if len(row) > 2 else ""
        status = row[5] if len(row) > 5 else ""

        if status.strip().lower() == "done":
            print(f"⏩ Row {i}: Already processed. Skipping.")
            continue

        website_doc_link = ""
        audio_doc_link = ""

        # Format date (keep only date, remove time)
        date_only = date.split()[0] if date else ""

        # 🌐 Process Website
        if website_url:
            try:
                print(f"\n🌐 Row {i}: Summarizing website: {website_url}")
                raw_text = extract_text_from_url(website_url)
                summary = summarize_with_openai(raw_text)
                name = format_website_name(website_url)
                doc_stream = create_website_doc(summary, f"{name} Website Summary")
                file_id = upload_docx_to_gdrive(
                    doc_stream, f"{name} Website Summary.docx"
                )
                website_doc_link = f"https://docs.google.com/document/d/{file_id}/edit"
                print("✅ Website summary uploaded.")
            except Exception as e:
                print(f"❌ Website error (row {i}): {e}")
                website_doc_link = "ERROR"

        # 🔊 Process Audio
        if audio_folder_link:
            try:
                print(f"\n🎧 Row {i}: Summarizing audio folder: {audio_folder_link}")
                folder_id = extract_folder_id(audio_folder_link)
                if not folder_id:
                    raise ValueError("Invalid folder link.")

                audio_file_id = get_first_m4a_file_id_in_folder(folder_id)
                if not audio_file_id:
                    raise FileNotFoundError("No .m4a file found in folder.")

                company_name = get_drive_folder_name(folder_id)

                audio_path = download_audio_from_drive(audio_file_id)

                # Check file size in bytes (25 MB = 25 * 1024 * 1024)
                file_size_bytes = os.path.getsize(audio_path)
                max_size_bytes = 25 * 1024 * 1024

                if file_size_bytes > max_size_bytes:
                    print(
                        f"⚠️ Audio file size {file_size_bytes / (1024*1024):.2f} MB exceeds 25 MB, splitting..."
                    )
                    chunks = split_audio(audio_path)
                else:
                    print(
                        f"ℹ️ Audio file size {file_size_bytes / (1024*1024):.2f} MB is under 25 MB, processing whole file."
                    )
                    chunks = [audio_path]

                transcripts = [transcribe_audio(chunk) for chunk in chunks]
                full_transcript = "\n".join(transcripts)
                summary_data = generate_summary(full_transcript)

                # Pass date_only (without time) to appear inside the document
                docx_file = create_audio_doc(summary_data, company_name, date_only)
                final_name = f"{company_name} Meeting Notes.docx"

                uploaded_id = upload_file_to_drive_in_memory(
                    docx_file, folder_id=AUDIO_DRIVE_FOLDER_ID, final_name=final_name
                )
                audio_doc_link = (
                    f"https://docs.google.com/document/d/{uploaded_id}/edit"
                )

                # Clean up chunk files if split
                if len(chunks) > 1:
                    for chunk_file in chunks:
                        if os.path.exists(chunk_file):
                            os.remove(chunk_file)

                # Always remove original audio file
                if os.path.exists(audio_path):
                    os.remove(audio_path)

                print("✅ Audio summary uploaded.")
            except Exception as e:
                print(f"❌ Audio error (row {i}): {e}")
                audio_doc_link = "ERROR"

        # 📝 Write results to columns D, E, F
        update_body = {"values": [[website_doc_link, audio_doc_link, "done"]]}
        service.spreadsheets().values().update(
            spreadsheetId=GOOGLE_SHEET_ID,
            range=f"Sheet1!D{i}:F{i}",
            valueInputOption="USER_ENTERED",
            body=update_body,
        ).execute()

    print("\n✅ All rows processed successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("❌ Script failed:", e)

# Helo
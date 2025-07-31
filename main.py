import os
import re
import tempfile

from Website.extract import extract_text_from_url
from Website.summarize import summarize_with_openai
from Website.document import create_docx_in_memory as create_website_doc
from Website.drive import upload_docx_to_gdrive

from Audio.transcription import transcribe_audio
from Audio.summarizer import generate_summary
from Audio.doc_generator import generate_docx as create_audio_doc
from Audio.drive_utils import upload_file_to_drive_in_memory, download_audio_from_drive
from Audio.config import GOOGLE_DRIVE_API_KEY 


def format_website_name(url):
    domain = re.sub(r"https?://(www\.)?", "", url).split("/")[0]
    parts = domain.split(".")
    ignore = {"com", "in", "net", "org", "www"}
    main_parts = [part for part in parts if part.lower() not in ignore]
    return main_parts[0].capitalize() if main_parts else "Website"



def extract_drive_file_id(link):
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", link)
    return match.group(1) if match else None


def process_website(url, custom_name=None):
    print(f"\n🌐 Processing website: {url}")
    raw_text = extract_text_from_url(url)
    summary = summarize_with_openai(raw_text)
    name = custom_name or format_website_name(url)
    doc_stream = create_website_doc(summary, f"{name} Website Summary")
    upload_docx_to_gdrive(doc_stream, f"{name} Website Summary.docx")
    print("✅ Website summary uploaded to Google Drive.")


def process_audio(drive_link, company_name, meeting_date):
    print(f"\n🔊 Processing audio for: {company_name} on {meeting_date}")
    file_id = extract_drive_file_id(drive_link)
    if not file_id:
        print("❌ Invalid Google Drive link.")
        return

    print("📥 Downloading audio...")
    audio_path = download_audio_from_drive(
        file_id, api_key=GOOGLE_DRIVE_API_KEY
    )

    print("📝 Transcribing audio...")
    transcript = transcribe_audio(audio_path)

    print("🧠 Summarizing transcript...")
    summary_data = generate_summary(transcript)

    print("📄 Generating .docx...")
    docx_file = create_audio_doc(summary_data, company_name, meeting_date)

    final_name = f"{company_name} Meeting Notes.docx"
    upload_file_to_drive_in_memory(
        docx_file, folder_id="1ngGsk7hSe-yOTUz17kfQLtTwXaWbSCMt", final_name=final_name
    )

    os.remove(audio_path)
    print("✅ Audio summary uploaded to Google Drive.")


def main():
    print("📦 Welcome to Summarizer Main Interface")

    website_url = input("\n🌐 Enter website URL (or leave blank): ").strip()
    website_name = input("🔤 Enter custom website name (optional): ").strip()

    audio_link = input("\n🔗 Enter audio Google Drive link (or leave blank): ").strip()
    audio_name = input("🏢 Enter company name (optional): ").strip()
    meeting_date = input("📅 Enter meeting date (dd-mm-yyyy, optional): ").strip()

    if not website_url and not audio_link:
        print("⚠️ Nothing to process. Please provide at least one input.")
        return

    if website_url:
        process_website(website_url, website_name)

    if audio_link:
        if not audio_name or not meeting_date:
            print("⚠️ Audio processing skipped. Company name and date are required.")
        else:
            process_audio(audio_link, audio_name, meeting_date)


if __name__ == "__main__":
    main()

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

# 🔐 Load environment variables from .env
load_dotenv()
AUDIO_DRIVE_FOLDER_ID = os.getenv(
    "AUDIO_DRIVE_FOLDER_ID"
)  # Shared Drive folder for audio docs


# 🏷 Format website name from a URL (extracts core domain)
def format_website_name(url):
    domain = re.sub(r"https?://(www\\.)?", "", url).split("/")[0]
    parts = domain.split(".")
    ignore = {"com", "in", "net", "org", "www"}
    main_parts = [part for part in parts if part.lower() not in ignore]
    return main_parts[0].capitalize() if main_parts else "Website"


# 🔗 Extracts file ID from a Google Drive shareable link
def extract_drive_file_id(link):
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", link)
    return match.group(1) if match else None


# 🌐 End-to-end processing of website content
def process_website(url, custom_name=None):
    print(f"\n🌐 Processing website: {url}")
    raw_text = extract_text_from_url(url)
    summary = summarize_with_openai(raw_text)
    name = custom_name or format_website_name(url)
    doc_stream = create_website_doc(summary, f"{name} Website Summary")
    upload_docx_to_gdrive(doc_stream, f"{name} Website Summary.docx")
    print("✅ Website summary uploaded to Google Drive.")


# 🔊 End-to-end processing of audio content
def process_audio(drive_link, company_name, meeting_date):
    print(f"\n🔊 Processing audio for: {company_name} on {meeting_date}")
    file_id = extract_drive_file_id(drive_link)
    if not file_id:
        print("❌ Invalid Google Drive link.")
        return

    print("📥 Downloading audio...")
    audio_path = download_audio_from_drive(file_id)

    print("🎧 Splitting audio into chunks (15 mins each)...")
    chunks = split_audio(audio_path)

    print("📝 Transcribing each chunk...")
    transcripts = [transcribe_audio(chunk) for chunk in chunks]
    full_transcript = "\n".join(transcripts)

    print("🧠 Summarizing transcript...")
    summary_data = generate_summary(full_transcript)

    print("📄 Generating .docx...")
    docx_file = create_audio_doc(summary_data, company_name, meeting_date)

    final_name = f"{company_name} Meeting Notes.docx"
    upload_file_to_drive_in_memory(
        docx_file, folder_id=AUDIO_DRIVE_FOLDER_ID, final_name=final_name
    )

    os.remove(audio_path)
    for chunk in chunks:
        os.remove(chunk)

    print("✅ Audio summary uploaded to Google Drive.")


# 🖥️ CLI entrypoint
def main():
    print("📦 Smart Summariser")

    # 🌐 Website inputs
    website_url = input("\n🌐 Enter website URL: ").strip()
    website_name = input("🔤 Enter custom website name (optional): ").strip()

    # 🎧 Audio inputs
    audio_link = input("\n🔗 Enter audio Google Drive link: ").strip()
    audio_name = input("🏢 Enter company name: ").strip()
    meeting_date = input("📅 Enter meeting date (dd-mm-yyyy): ").strip()

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

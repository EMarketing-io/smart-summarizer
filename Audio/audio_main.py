import os
import shutil
from pydub import AudioSegment
import re
from Audio.drive_utils import upload_file_to_drive_in_memory, download_audio_from_drive
from Audio.transcription import transcribe_audio
from Audio.summarizer import generate_summary
from Audio.doc_generator import generate_docx
from Audio.config import (
    GOOGLE_DRIVE_API_KEY,
    GOOGLE_DRIVE_FOLDER_ID,
)
import io


def extract_drive_file_id(drive_link):
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", drive_link)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Google Drive link. Could not extract file ID.")


def split_audio(audio_path, chunk_length_ms=5 * 60 * 1000):
    audio = AudioSegment.from_file(audio_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i : i + chunk_length_ms]
        chunk_path = f"{audio_path}_part{i // chunk_length_ms}.mp3"
        chunk.export(chunk_path, format="mp3")
        chunks.append(chunk_path)
    return chunks


def main():
    company_name = input("Enter the company name: ").strip()
    meeting_date = input("Enter the date of the meeting (dd-mm-yyyy): ").strip()
    drive_link = input("Enter the Google Drive link of the audio file: ").strip()

    file_id = extract_drive_file_id(drive_link)

    if not file_id:
        raise Exception("Invalid Google Drive link")

    print("📥 Downloading audio...")
    audio_path = download_audio_from_drive(file_id, GOOGLE_DRIVE_API_KEY)

    print("🎧 Splitting audio into smaller chunks...")
    chunks = split_audio(audio_path)

    print("📝 Transcribing chunks...")
    transcripts = [transcribe_audio(chunk) for chunk in chunks]
    transcript_text = "\n".join(transcripts)

    print("🧠 Generating summary...")
    summary_data = generate_summary(transcript_text)

    print("📄 Creating DOCX file in memory...")
    docx_file_data = generate_docx(summary_data, company_name, meeting_date)

    file_name = f"{company_name} Meeting Notes.docx"

    print("⬆️ Uploading DOCX to Google Drive...")
    uploaded_link = upload_file_to_drive_in_memory(
        docx_file_data, GOOGLE_DRIVE_FOLDER_ID, final_name=file_name
    )
    print(f"✅ File uploaded to Google Drive: {uploaded_link}")

    os.remove(audio_path)
    for chunk in chunks:
        os.remove(chunk)
    print("✅ All done! File uploaded to Google Drive.")


if __name__ == "__main__":
    main()

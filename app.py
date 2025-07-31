import streamlit as st
import tempfile
import re

from Website.extract import extract_text_from_url
from Website.summarize import summarize_with_openai
from Website.document import create_docx_in_memory as create_website_doc
from Website.drive import upload_docx_to_gdrive

from Audio.transcription import transcribe_audio
from Audio.summarizer import generate_summary
from Audio.doc_generator import generate_docx as create_audio_doc
from Audio.drive_utils import upload_file_to_drive_in_memory, download_audio_from_drive
from Audio.config import GOOGLE_DRIVE_API_KEY

st.set_page_config(page_title="SmartSummarizer", layout="wide", page_icon="🧠")
st.markdown(
    "<h1 style='text-align: center;'>🧠 SmartSummarizer</h1>", unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: center;'>Turn 🌐 websites and 🎧 meetings into professional summaries and upload to Google Drive!</p>",
    unsafe_allow_html=True,
)


def format_website_name(url):
    domain = re.sub(r"https?://(www\.)?", "", url).split("/")[0]
    parts = domain.split(".")
    ignore = {"com", "in", "net", "org", "www"}
    main_parts = [part for part in parts if part.lower() not in ignore]
    return main_parts[0].capitalize() if main_parts else "Website"



def extract_drive_file_id(link):
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", link)
    return match.group(1) if match else None


col1, col2 = st.columns(2)

with col1:
    st.subheader("🌐 Website Summarization")
    website_url = st.text_input("Website URL", placeholder="e.g. https://example.com")
    website_name = st.text_input(
        "Custom Website Name (optional)", placeholder="e.g. Acme Corp"
    )

with col2:
    st.subheader("🎧 Audio Summarization")
    audio_link = st.text_input(
        "Google Drive Link to Audio",
        placeholder="e.g. https://drive.google.com/file/d/...",
    )
    audio_company = st.text_input("Company Name", placeholder="e.g. Acme Corp")
    audio_date = st.text_input("Meeting Date", placeholder="dd-mm-yyyy")

if st.button("🚀 Summarize & Upload"):
    try:
        if not website_url and not audio_link:
            st.warning("😅 Please provide at least one input — Website or Audio.")
        else:
            if website_url:
                with st.spinner("🕸️ Extracting and summarizing website..."):
                    raw_text = extract_text_from_url(website_url)
                    summary = summarize_with_openai(raw_text)
                    name = website_name or format_website_name(website_url)
                    doc_stream = create_website_doc(summary, f"{name} Website Summary")
                    upload_docx_to_gdrive(doc_stream, f"{name} Website Summary.docx")
                    st.success("✅ Website summary uploaded to Google Drive!")

            if audio_link:
                if not audio_company or not audio_date:
                    st.warning(
                        "🎧 Please enter both Company Name and Meeting Date for audio."
                    )
                else:
                    with st.spinner("🎙️ Transcribing and summarizing audio..."):
                        file_id = extract_drive_file_id(audio_link)
                        if not file_id:
                            st.error("❌ Invalid Google Drive link format.")
                        else:
                            audio_path = download_audio_from_drive(
                                file_id, api_key=GOOGLE_DRIVE_API_KEY
                            )
                            transcript = transcribe_audio(audio_path)
                            summary = generate_summary(transcript)
                            docx_file = create_audio_doc(
                                summary, audio_company, audio_date
                            )
                            final_name = f"{audio_company} Meeting Notes.docx"
                            upload_file_to_drive_in_memory(
                                docx_file,
                                folder_id="1ngGsk7hSe-yOTUz17kfQLtTwXaWbSCMt",
                                final_name=final_name,
                            )
                            st.success("✅ Audio summary uploaded to Google Drive!")
    except Exception as e:
        st.error(f"❌ Something went wrong: {e}")

# 🧠 SmartSummarizer

SmartSummarizer is a powerful productivity tool that converts **websites** and **meeting audio files** into professional, structured summaries — and uploads them to your **Google Drive** in `.docx` format.

Whether you’re analyzing competitors’ websites or reviewing business meetings, SmartSummarizer turns raw data into clean documentation using OpenAI’s APIs.

---

## 🚀 Features

- 🌐 **Website Summarizer**

  - Extracts text from any public URL.
  - Uses GPT to summarize content into detailed business insights.
  - Includes sections like: Purpose, USP, Reviews, Products, Offers, etc.

- 🎧 **Audio Summarizer**

  - Downloads audio files from Google Drive.
  - Automatically splits large files (>15 min) to comply with OpenAI limits.
  - Uses Whisper for transcription and GPT for structured meeting notes (MoM, To-Do, Action Plans).

- 📄 **Document Export**

  - Summaries are converted into clean `.docx` files with bullet points, headings, and bold formatting.
  - Files are uploaded directly to your configured Google Drive folders.

- 🖥️ **Interfaces**
  - ✅ CLI: `python main.py`
  - ✅ Web UI: `streamlit run app.py`

---

## 📁 Project Structure

```
smart-summarizer/
├── audio/                # Audio transcription + summarization modules
├── website/              # Website scraping + summarization modules
├── config/               # Google OAuth credentials and tokens
├── app.py                # Streamlit web interface
├── main.py               # CLI interface
├── .env                  # Environment variables (API keys, folder IDs)
├── requirements.txt      # Python dependencies
```

---

## 🔧 Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/smart-summarizer.git
cd smart-summarizer
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Make sure `ffmpeg` is installed and accessible from PATH (required for audio chunking).

### 3. Configure `.env`

Create a `.env` file with the following keys:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Google Drive
GOOGLE_CREDENTIALS_PATH=config/google_oauth_credentials.json
GOOGLE_TOKEN_PATH=config/token.pickle

DRIVE_FOLDER_WEBSITE=your-folder-id
DRIVE_FOLDER_AUDIO=your-folder-id
DRIVE_PUBLIC_API_KEY=your-public-api-key
```

> `google_oauth_credentials.json` should be downloaded from Google Cloud Console and placed in `/config`.

---

## 🧪 Usage

### 🖥️ CLI Mode

```bash
python main.py
```

Follow the prompts to summarize a website or audio file.

### 🌐 Web App (Streamlit)

```bash
streamlit run app.py
```

Use the UI to upload and summarize content easily.

---

## 🛡️ Privacy & Security

- All API keys and credentials are kept in `.env` and excluded from version control.
- Only metadata and text-based summaries are stored — raw content is deleted after processing.

---

## 🧩 Dependencies

- OpenAI (Whisper + ChatGPT)
- Google Drive API
- python-docx
- BeautifulSoup4
- Streamlit
- Pydub + FFmpeg

---

import requests
from bs4 import BeautifulSoup

# 🌐 Extracts clean, readable text content from a given website URL
def extract_text_from_url(url):
    # 🔗 Send a GET request to fetch the web page content
    response = requests.get(url)

    # 🧽 Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # 🚫 Remove unwanted script and style elements to avoid noise
    for script in soup(["script", "style"]):
        script.decompose()

    # 📃 Extract the visible text with newline separators
    text = soup.get_text(separator="\n")

    # 🧹 Clean up: strip each line and remove empty ones
    lines = [line.strip() for line in text.splitlines()]
    cleaned_text = "\n".join(line for line in lines if line)

    # 🧾 Return the fully cleaned body text
    return cleaned_text

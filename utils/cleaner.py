# utils/cleaner.py
import re
from bs4 import BeautifulSoup

def clean_text(text):
    if not text:
        return ""

    # Remove HTML tags
    text = BeautifulSoup(text, "html.parser").get_text()

    # Remove Markdown-style links [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # Remove special characters, extra newlines
    text = re.sub(r'\s+', ' ', text).strip()

    return text

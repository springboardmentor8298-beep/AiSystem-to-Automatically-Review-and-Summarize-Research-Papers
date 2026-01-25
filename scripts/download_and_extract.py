import os
import requests
import pdfplumber
import re

# ---------------------------------------
# SAVE FILES OUTSIDE PROJECT (IMPORTANT)
# ---------------------------------------
BASE_STORAGE = os.path.join(os.path.expanduser("~"), "paper_summarizer_storage")

PDF_DIR = os.path.join(BASE_STORAGE, "pdfs")
TEXT_DIR = os.path.join(BASE_STORAGE, "text")

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)


# ---------------------------------------
# TEXT CLEANING (CRITICAL FIX)
# ---------------------------------------
def clean_extracted_text(text):
    """
    Clean raw PDF text to improve summarization quality
    """

    if not text:
        return ""

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove references section
    text = re.split(r'\bREFERENCES\b|\bReferences\b|\bBibliography\b', text)[0]

    # Remove figure/table captions
    text = re.sub(r'(Figure|Table)\s+\d+.*?(?=\.)', '', text)

    # Remove excessive numbers / percentages blocks
    text = re.sub(r'\b\d+(\.\d+)?%\b', '', text)

    # Remove author lists (heuristic)
    text = re.sub(r'([A-Z][a-z]+,\s?[A-Z]\.){2,}', '', text)

    # Fix broken hyphenated words
    text = re.sub(r'-\s+', '', text)

    # Remove leftover symbols
    text = re.sub(r'[•▪◆◦■]', '', text)

    return text.strip()


def download_and_extract(pdf_url):
    """
    Download PDF from URL and extract CLEANED text.
    Returns cleaned text string.
    """

    filename = pdf_url.split("/")[-1].split("?")[0]
    pdf_path = os.path.join(PDF_DIR, filename)
    txt_path = os.path.join(TEXT_DIR, filename.replace(".pdf", ".txt"))

    # Download PDF
    response = requests.get(pdf_url, timeout=60)
    response.raise_for_status()

    with open(pdf_path, "wb") as f:
        f.write(response.content)

    # Extract raw text
    raw_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                raw_text += page_text + "\n"

    # 🔥 CLEAN TEXT HERE
    cleaned_text = clean_extracted_text(raw_text)

    # Save cleaned text
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    return cleaned_text

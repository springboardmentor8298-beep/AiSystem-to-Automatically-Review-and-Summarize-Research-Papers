import os
import requests
import pdfplumber
import re

BASE_STORAGE = os.path.join(os.path.expanduser("~"), "paper_summarizer_storage")
PDF_DIR = os.path.join(BASE_STORAGE, "pdfs")
TEXT_DIR = os.path.join(BASE_STORAGE, "text")

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)


def clean_extracted_text(text: str) -> str:
    if not text:
        return ""

    # Preserve paragraphs
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove references
    text = re.split(r'\bREFERENCES\b|\bBibliography\b', text, flags=re.I)[0]

    # Remove figure/table captions
    text = re.sub(r'(Figure|Table)\s+\d+[:.]?.*', '', text)

    # Fix hyphenated line breaks
    text = re.sub(r'-\n', '', text)

    # Fix camelCase joins
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)

    # Remove URLs
    text = re.sub(r'http\S+', '', text)

    return text.strip()


def download_and_extract(pdf_url: str) -> str:
    filename = pdf_url.split("/")[-1].split("?")[0]
    pdf_path = os.path.join(PDF_DIR, filename)

    try:
        response = requests.get(pdf_url, timeout=40, headers={
            "User-Agent": "Mozilla/5.0"
        })
        response.raise_for_status()
    except Exception:
        print(f"[WARN] PDF blocked: {pdf_url}")
        return ""

    with open(pdf_path, "wb") as f:
        f.write(response.content)

    raw_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    raw_text += t + "\n\n"
    except Exception:
        return ""

    return clean_extracted_text(raw_text)

import os
import requests
import pdfplumber

PDF_DIR = "data/pdfs"
TEXT_DIR = "data/text"

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)


def download_and_extract(pdf_url):
    """
    Download PDF from URL and extract text.
    Returns extracted text as string.
    """

    filename = pdf_url.split("/")[-1]
    pdf_path = os.path.join(PDF_DIR, filename)
    txt_path = os.path.join(TEXT_DIR, filename.replace(".pdf", ".txt"))

    # Download PDF
    response = requests.get(pdf_url, timeout=30)
    response.raise_for_status()

    with open(pdf_path, "wb") as f:
        f.write(response.content)

    # Extract text
    extracted_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"

    # Save text
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    return extracted_text

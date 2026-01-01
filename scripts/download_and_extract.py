import requests
import pdfplumber
import os

PDF_DIR = "data/pdfs"
TEXT_DIR = "data/text"

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)

def download_pdf(pdf_url, filename):
    pdf_path = os.path.join(PDF_DIR, filename)

    response = requests.get(pdf_url, timeout=20)
    response.raise_for_status()

    with open(pdf_path, "wb") as f:
        f.write(response.content)

    return pdf_path

def extract_text_from_pdf(pdf_path, text_filename):
    text_path = os.path.join(TEXT_DIR, text_filename)

    all_text = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text.append(text)

    final_text = "\n".join(all_text)

    with open(text_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    return text_path

if __name__ == "__main__":
    # Sample open-access PDF for testing
    sample_pdf_url = "https://arxiv.org/pdf/1706.03762.pdf"
    pdf_file = "sample_attention_is_all_you_need.pdf"
    text_file = "sample_attention_is_all_you_need.txt"

    print("Downloading PDF...")
    pdf_path = download_pdf(sample_pdf_url, pdf_file)

    print("Extracting text...")
    text_path = extract_text_from_pdf(pdf_path, text_file)

    print("PDF saved at:", pdf_path)
    print("Extracted text saved at:", text_path)

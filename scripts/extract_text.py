import fitz
import os

PDF_DIR = "data/pdfs"
TEXT_DIR = "data/extracted_text"

os.makedirs(TEXT_DIR, exist_ok=True)

def extract_text():
    for pdf in os.listdir(PDF_DIR):
        if pdf.endswith(".pdf"):
            doc = fitz.open(os.path.join(PDF_DIR, pdf))
            text = ""

            for page in doc:
                text += page.get_text()

            with open(os.path.join(TEXT_DIR, pdf.replace(".pdf", ".txt")), "w", encoding="utf-8") as f:
                f.write(text)

            print(f"Extracted text: {pdf}")

if __name__ == "__main__":
    extract_text()

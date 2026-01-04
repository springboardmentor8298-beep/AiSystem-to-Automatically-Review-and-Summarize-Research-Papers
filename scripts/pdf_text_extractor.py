import os
import json
import fitz  # PyMuPDF

PDF_DIR = "pdfs/speech_recognisation"
OUTPUT_FILE = "extracted_text/raw_text.json"

data = []

for file in os.listdir(PDF_DIR):
    if file.endswith(".pdf"):
        text = ""
        doc = fitz.open(os.path.join(PDF_DIR, file))
        for page in doc:
            text += page.get_text()
        data.append({
            "pdf_file": file,
            "text": text
        })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

print("✅ Raw text extracted")

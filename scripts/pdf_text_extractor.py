import sys
import os
import json
import fitz # PyMuPDF 

topic = sys.argv[1].strip().replace(" ", "_").lower() 
INPUT_PDF_DIR = f"pdfs/{topic}" 
OUTPUT_FILE = f"extracted_text/{topic}_raw_text.json" 
PDF_DIR = INPUT_PDF_DIR 
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
            os.makedirs("extracted_text", exist_ok=True) 
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=4) 
print("✅ Raw text extracted for topic:", topic)
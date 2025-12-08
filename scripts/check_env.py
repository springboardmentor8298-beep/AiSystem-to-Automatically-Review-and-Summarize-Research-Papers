# scripts/check_env.py
"""
Simplified environment & PDF extraction check.
Run after activating venv to verify core installs and that PDF extraction works.
"""
import sys
from pathlib import Path

print("Python:", sys.version)

libs = [
    ("requests", "requests"),
    ("pdfplumber", "pdfplumber"),
    ("PyMuPDF", "fitz"),
    ("langchain", "langchain"),
    ("gradio", "gradio"),
    ("pytest", "pytest"),
    ("pydantic", "pydantic"),
    ("transformers", "transformers")
]

for name, module in libs:
    try:
        __import__(module)
        print(f"OK import: {name}")
    except Exception as e:
        print(f"ERR import {name}: {e}")

# Create a tiny sample PDF using PyMuPDF (fitz) if it doesn't exist
sample_pdf = Path("data/pdfs/sample_test.pdf")
sample_pdf.parent.mkdir(parents=True, exist_ok=True)
if not sample_pdf.exists():
    try:
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "PDF extraction test. Hello AI Internship.")
        doc.save(str(sample_pdf))
        doc.close()
        print("Created sample_test.pdf via PyMuPDF.")
    except Exception as e:
        print("Could not create sample PDF via PyMuPDF:", e)

# Try extracting text with pdfplumber
try:
    import pdfplumber
    with pdfplumber.open(str(sample_pdf)) as pdf:
        texts = [p.extract_text() for p in pdf.pages]
    print("pdfplumber extracted:", texts)
except Exception as e:
    print("pdfplumber extraction failed:", e)

# Try extracting text with PyMuPDF
try:
    import fitz
    doc = fitz.open(str(sample_pdf))
    texts2 = [p.get_text() for p in doc]
    doc.close()
    print("PyMuPDF extracted:", texts2)
except Exception as e:
    print("PyMuPDF extraction failed:", e)

print("\nCheck complete - if you see OK import lines and extracted text, Day 1 & 2 are complete.")

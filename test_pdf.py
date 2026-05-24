# test_pdf.py
import fitz

pdf_path = "storage/pdfs/2306.04338v1.pdf"  # Path to one of your PDFs

try:
    doc = fitz.open(pdf_path)
    print(f"PDF has {len(doc)} pages")
    full_text = ""
    for i, page in enumerate(doc):
        text = page.get_text()
        full_text += text
        print(f"Page {i+1}: {len(text)} chars")
    doc.close()
    print(f"\nTotal text extracted: {len(full_text)} chars")
    print(f"First 500 chars:\n{full_text[:500]}")
except Exception as e:
    print(f"Error: {e}")
import fitz  # PyMuPDF
import os
import requests
import json
from io import BytesIO

TEXT_DIR = "app/papers/text"

def extract_all_papers(papers):
    """
    Extracts text from PDF URLs using in-memory processing
    and saves both extracted text and metadata separately.
    """

    os.makedirs(TEXT_DIR, exist_ok=True)

    for idx, paper in enumerate(papers, start=1):
        title = paper.get("title", f"Paper {idx}")
        url = paper.get("url")

        print(f"📄 Processing paper {idx}: {title}")

        try:
            # Fetch PDF (NO local PDF storage)
            res = requests.get(url, timeout=30)
            res.raise_for_status()

            # Open PDF from memory
            doc = fitz.open(stream=BytesIO(res.content), filetype="pdf")

            # Extract full text
            text = ""
            for page in doc:
                text += page.get_text()

            # Save extracted text
            text_path = f"{TEXT_DIR}/paper_{idx}.txt"
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(text)

            # Save metadata separately
            meta_path = f"{TEXT_DIR}/paper_{idx}_meta.json"
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(paper, f, indent=2)

            print(f"✅ Saved text → {text_path}")
            print(f"🗂️ Saved metadata → {meta_path}")

        except Exception as e:
            print(f"❌ Error processing {title}: {e}")
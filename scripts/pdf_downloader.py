import json
import os
import requests

METADATA_DIR = "data/metadata"
PDF_DIR = "data/pdfs"

os.makedirs(PDF_DIR, exist_ok=True)

def download_pdfs():
    for file in os.listdir(METADATA_DIR):
        with open(os.path.join(METADATA_DIR, file), "r", encoding="utf-8") as f:
            papers = json.load(f)

        for paper in papers:
            title = paper.get("title", "paper").replace(" ", "_").replace("/", "")
            pdf_url = ""

            # 1️⃣ Try openAccessPdf
            open_pdf = paper.get("openAccessPdf", {})
            if open_pdf.get("url"):
                pdf_url = open_pdf["url"]

            # 2️⃣ Fallback to ArXiv
            else:
                arxiv_id = paper.get("externalIds", {}).get("ArXiv")
                if arxiv_id:
                    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

            if not pdf_url:
                print(f"Skipped (no PDF source): {title}")
                continue

            try:
                r = requests.get(pdf_url, timeout=15)
                if r.status_code == 200:
                    with open(os.path.join(PDF_DIR, f"{title}.pdf"), "wb") as f:
                        f.write(r.content)
                    print(f"Downloaded PDF: {title}")
                else:
                    print(f"Failed download: {title}")
            except Exception as e:
                print(f"Error downloading {title}: {e}")

if __name__ == "__main__":
    download_pdfs()

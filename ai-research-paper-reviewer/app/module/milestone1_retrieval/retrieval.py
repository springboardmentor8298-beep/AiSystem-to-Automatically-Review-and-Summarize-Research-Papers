import os
import json
import time
import requests
from dotenv import load_dotenv

# =========================
# ENV + CONFIG
# =========================
load_dotenv()

API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
if not API_KEY:
    raise RuntimeError("Semantic Scholar API key not found in .env")

BASE_URL = "https://api.semanticscholar.org/graph/v1"
HEADERS = {"x-api-key": API_KEY}

SAVE_DIR = "papers"
META_FILE = "papers_metadata.json"

os.makedirs(SAVE_DIR, exist_ok=True)

# =========================
# PAPER SEARCH
# =========================
def search_papers(topic, limit=5):
    print(f"[INFO] Searching papers for topic: {topic}")

    url = f"{BASE_URL}/paper/search"
    params = {
        "query": topic,
        "limit": limit,
        "fields": "title,authors,year,openAccessPdf"
    }

    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()

    return response.json().get("data", [])

# =========================
# PDF DOWNLOAD
# =========================
def download_pdf(pdf_url, filename):
    response = requests.get(pdf_url, stream=True)
    response.raise_for_status()

    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)

# =========================
# PIPELINE
# =========================
def run_milestone_1(topic, limit=5):
    papers = search_papers(topic, limit)
    metadata = []

    for idx, paper in enumerate(papers, start=1):
        pdf_info = paper.get("openAccessPdf")
        if not pdf_info or not pdf_info.get("url"):
            print(f"[SKIP] No PDF available: {paper.get('title')}")
            continue

        pdf_url = pdf_info["url"]
        filename = f"{SAVE_DIR}/paper_{idx}.pdf"

        print(f"[DOWNLOAD] {paper.get('title')}")
        download_pdf(pdf_url, filename)

        metadata.append({
            "title": paper.get("title"),
            "authors": [a["name"] for a in paper.get("authors", [])],
            "year": paper.get("year"),
            "pdf_path": filename
        })

        time.sleep(1)  # polite API usage

    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n[SUCCESS] Downloaded {len(metadata)} papers")
    print(f"[DATASET] Metadata saved to {META_FILE}")

# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    topic_input = input("Enter research topic: ")
    run_milestone_1(topic_input, limit=5)

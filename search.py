# 








import os
import json
import time
import requests
from dotenv import load_dotenv
import pymupdf4llm

# =========================
# CONFIG
# =========================
load_dotenv()

SEMANTIC_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
PAPERS_FOLDER = "papers"
DATASET_FILE = "dataset.json"

MAX_SUCCESSFUL_PAPERS = 10
BATCH_SIZE = 50
MAX_RETRIES = 3

os.makedirs(PAPERS_FOLDER, exist_ok=True)

# =========================
# SEMANTIC SCHOLAR REST API
# =========================
def search_semantic_scholar(query, limit=50, offset=0):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "offset": offset,
        "fields": "title,authors,year,abstract,openAccessPdf,citationCount"
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    if SEMANTIC_API_KEY:
        headers["x-api-key"] = SEMANTIC_API_KEY

    response = requests.get(url, params=params, headers=headers, timeout=20)
    response.raise_for_status()
    return response.json().get("data", [])

# =========================
# PDF DOWNLOAD
# =========================
def download_pdf(pdf_url, name_prefix):
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in name_prefix)[:80]
    path = os.path.join(PAPERS_FOLDER, f"{safe_name}.pdf")

    try:
        r = requests.get(pdf_url, stream=True, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            with open(path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            return path
    except:
        pass

    return None

# =========================
# PDF TEXT EXTRACTION
# =========================
def extract_sections(pdf_path):
    try:
        text = pymupdf4llm.to_markdown(pdf_path)
        sections = {}
        current = "Full Text"

        for line in text.split("\n"):
            line = line.strip()
            if line.startswith(("# ", "## ", "### ")):
                current = line.lstrip("# ").strip()
            elif line:
                sections.setdefault(current, "")
                sections[current] += line + " "

        return {k: v.strip() for k, v in sections.items()}
    except:
        return {"error": "Extraction failed"}

# =========================
# MAIN COLLECTION LOGIC
# =========================
def collect_papers(topic):
    print(f"\n🔍 Searching for: {topic}")
    print(f"🎯 Goal: {MAX_SUCCESSFUL_PAPERS} open-access PDFs\n")

    collected = []
    offset = 0
    retries = 0

    while len(collected) < MAX_SUCCESSFUL_PAPERS and retries < MAX_RETRIES:
        try:
            print(f"Fetching papers (offset={offset})...")
            results = search_semantic_scholar(topic, limit=BATCH_SIZE, offset=offset)

            if not results:
                print("No more results found.")
                break

            for paper in results:
                if len(collected) >= MAX_SUCCESSFUL_PAPERS:
                    break

                pdf_info = paper.get("openAccessPdf")
                if not pdf_info or "url" not in pdf_info:
                    continue

                title = paper.get("title", "Untitled")
                print(f"📄 Trying: {title}")

                pdf_path = download_pdf(pdf_info["url"], f"{len(collected)+1}_{title}")
                if not pdf_path:
                    continue

                sections = extract_sections(pdf_path)

                collected.append({
                    "title": title,
                    "authors": [a["name"] for a in paper.get("authors", [])],
                    "year": paper.get("year"),
                    "abstract": paper.get("abstract") or "No abstract",
                    "citations": paper.get("citationCount", 0),
                    "pdf_file": os.path.basename(pdf_path),
                    "sections": sections
                })

                print(f"✅ Added ({len(collected)}/{MAX_SUCCESSFUL_PAPERS})")

            offset += BATCH_SIZE
            time.sleep(2)

        except Exception as e:
            retries += 1
            print(f"⚠ Temporary error: {e}")
            print("⏳ Waiting 5 seconds...\n")
            time.sleep(5)

    return collected

# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    print("\n🧠 AI Paper Reviewer – Smart Open-Access Collector\n")

    topic = input("Enter research topic: ").strip()
    if not topic:
        topic = "attention is all you need"

    papers = collect_papers(topic)

    if not papers:
        print("\n❌ No downloadable open-access papers found.")
    else:
        with open(DATASET_FILE, "w", encoding="utf-8") as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)

        print("\n🎉 SUCCESS!")
        print(f"• Papers collected: {len(papers)}")
        print(f"• PDFs saved in: {PAPERS_FOLDER}/")
        print(f"• Dataset saved: {DATASET_FILE}")
        print("\n➡ Ready for Milestone 3 (LLM Analysis)")

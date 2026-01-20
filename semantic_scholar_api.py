from dotenv import load_dotenv
import requests
import json
import os
import time
import sys

load_dotenv()
# --------------------------------------------------
# Load API key securely from environment variable
# --------------------------------------------------
API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

if not API_KEY:
    raise ValueError(
        "API key not found. Please set SEMANTIC_SCHOLAR_API_KEY as an environment variable."
    )

HEADERS = {
    "x-api-key": API_KEY
}

BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

# --------------------------------------------------
# Take topic input
# --------------------------------------------------
topic = sys.argv[1].strip()
topic_name = topic.replace(" ", "_").lower()

# --------------------------------------------------
# Create required folders
# --------------------------------------------------
os.makedirs("papers_json", exist_ok=True)
os.makedirs(f"pdfs/{topic_name}", exist_ok=True)
os.makedirs("dataset", exist_ok=True)

# --------------------------------------------------
# API request parameters
# --------------------------------------------------
params = {
    "query": topic,
    "limit": 10,
    "fields": "title,authors,year,abstract,url,openAccessPdf"
}

# --------------------------------------------------
# Fetch papers from Semantic Scholar
# --------------------------------------------------
response = requests.get(BASE_URL, headers=HEADERS, params=params)
response.raise_for_status()

papers = response.json().get("data", [])

# --------------------------------------------------
# Save raw API JSON
# --------------------------------------------------
raw_json_path = f"papers_json/{topic_name}.json"
with open(raw_json_path, "w", encoding="utf-8") as f:
    json.dump(papers, f, indent=4)

print(f"✅ Raw data saved to {raw_json_path}")

# --------------------------------------------------
# Download PDFs and prepare dataset
# --------------------------------------------------
final_dataset = []
pdf_count = 0

for paper in papers:
    pdf_url = paper.get("openAccessPdf", {}).get("url")

    if pdf_url:
        pdf_count += 1
        pdf_path = f"pdfs/{topic_name}/paper{pdf_count}.pdf"

        try:
            pdf_response = requests.get(pdf_url)
            pdf_response.raise_for_status()

            with open(pdf_path, "wb") as f:
                f.write(pdf_response.content)

            final_dataset.append({
                "title": paper.get("title"),
                "authors": [author.get("name") for author in paper.get("authors", [])],
                "year": paper.get("year"),
                "abstract": paper.get("abstract"),
                "paper_url": paper.get("url"),
                "pdf_path": pdf_path
            })

            print(f"📄 Downloaded: {pdf_path}")

            # Respect API rate limit (1 request per second)
            time.sleep(1)

        except Exception as e:
            print(f"❌ Failed to download PDF: {e}")

# --------------------------------------------------
# Save analysis-ready dataset
# --------------------------------------------------
dataset_path = "dataset/papers_dataset.json"
with open(dataset_path, "w", encoding="utf-8") as f:
    json.dump(final_dataset, f, indent=4)

print(f"\n✅ Dataset prepared successfully: {dataset_path}")



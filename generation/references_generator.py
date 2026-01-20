import json
import os
import sys

topic = sys.argv[1].strip().replace(" ", "_").lower()
DATASET_FILE = "dataset/papers_dataset.json"
OUTPUT_DIR = f"generated_review/{topic}"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(DATASET_FILE, "r", encoding="utf-8") as f:
    papers = json.load(f)

references = []

for paper in papers:
    authors = ", ".join(paper.get("authors", []))
    year = paper.get("year", "n.d.")
    title = paper.get("title", "")
    url = paper.get("paper_url", "")
    references.append(f"{authors} ({year}). {title}. Retrieved from {url}")

# ✅ Fallback (CRITICAL)
if not references:
    references.append(
        "No valid open-access papers were available for reference generation."
    )

with open(f"{OUTPUT_DIR}/references.txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join(references))

print("✅ References generated (APA style)")

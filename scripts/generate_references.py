import json
import os

META_DIR = "data/metadata"
OUT_DIR = "data/generated/final"
OUT_FILE = os.path.join(OUT_DIR, "references.txt")

os.makedirs(OUT_DIR, exist_ok=True)

references = []

for file in os.listdir(META_DIR):
    if not file.endswith(".json"):
        continue

    with open(os.path.join(META_DIR, file), "r", encoding="utf-8") as f:
        papers = json.load(f)

    for paper in papers:
        title = paper.get("title", "Untitled")
        year = paper.get("year", "n.d.")
        authors = paper.get("authors", [])

        # Authors are already strings
        if isinstance(authors, list) and len(authors) > 0:
            author_str = ", ".join(authors[:3])
        else:
            author_str = "Unknown Author"

        reference = f"{author_str} ({year}). {title}."
        references.append(reference)

with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(references))

print("APA-style references generated successfully.")

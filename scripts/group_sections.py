import os
import json

SECTION_DIR = "data/sections"
OUTPUT_DIR = "data/generated"

os.makedirs(OUTPUT_DIR, exist_ok=True)

SECTION_KEYS = ["abstract", "introduction", "method", "results", "conclusion"]

grouped = {key: [] for key in SECTION_KEYS}

for file in os.listdir(SECTION_DIR):
    if not file.endswith(".json"):
        continue

    with open(os.path.join(SECTION_DIR, file), "r", encoding="utf-8") as f:
        paper = json.load(f)

    for key in SECTION_KEYS:
        if key in paper and paper[key].strip():
            grouped[key].append(paper[key].strip())

# Save grouped text
for key, texts in grouped.items():
    with open(os.path.join(OUTPUT_DIR, f"{key}.txt"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(texts))

    print(f"{key.upper()} grouped: {len(texts)} papers")

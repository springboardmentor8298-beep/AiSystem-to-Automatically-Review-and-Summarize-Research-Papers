import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from generation.model_loader import generate_text

# -----------------------
# INPUT
# -----------------------
topic = sys.argv[1].strip().replace(" ", "_").lower()

OUTPUT_DIR = f"generated_review/{topic}"
SECTIONS_FILE = f"extracted_text/{topic}_section_wise_text.json"
KEYWORDS_FILE = f"analysis/{topic}_keywords.json"
DATASET_FILE = "dataset/papers_dataset.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------
# LOAD KEYWORDS
# -----------------------
keywords = []
if os.path.exists(KEYWORDS_FILE):
    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        keywords = [k.get("keyword") for k in data if k.get("keyword")]

keywords_text = ", ".join(keywords[:6]) or "machine learning, social media analytics, user behavior"

# -----------------------
# LOAD SECTION DATA
# -----------------------
section_papers = []
if os.path.exists(SECTIONS_FILE):
    with open(SECTIONS_FILE, "r", encoding="utf-8") as f:
        section_papers = json.load(f)

# -----------------------
# ABSTRACT
# -----------------------
abstract_context = [
    p.get("abstract") for p in section_papers if p.get("abstract")
]

if not abstract_context:
    abstract_context = [
        "Recent research on Instagram focuses on engagement prediction, content recommendation, user behavior modeling, and sentiment analysis."
    ]

abstract_prompt = f"""
Write a concise academic abstract for a literature review on {topic}.

Keywords: {keywords_text}

Context:
{' '.join(abstract_context[:2])[:600]}

Summarize trends, methods, and findings in formal academic tone.
"""

abstract = generate_text(
    abstract_prompt,
    max_new_tokens=120
)

with open(f"{OUTPUT_DIR}/abstract.txt", "w", encoding="utf-8") as f:
    f.write(abstract.strip())

print("✅ Abstract generated")

# -----------------------
# METHODS
# -----------------------
methods_context = [
    p.get("methods") for p in section_papers if p.get("methods")
]

if not methods_context:
    methods_context = [
        "Studies commonly use transformers, graph neural networks, CNNs, and LSTM models trained on Instagram datasets with supervised and self-supervised learning."
    ]

methods_prompt = f"""
Write the Methods section of a literature review on {topic}.

Context:
{' '.join(methods_context[:2])[:600]}

Describe models, datasets, and training techniques.
"""

methods = generate_text(
    methods_prompt,
    max_new_tokens=140
)

with open(f"{OUTPUT_DIR}/methods.txt", "w", encoding="utf-8") as f:
    f.write(methods.strip())

print("✅ Methods generated")

# -----------------------
# RESULTS
# -----------------------
years = []
titles = []

if os.path.exists(DATASET_FILE):
    with open(DATASET_FILE, "r", encoding="utf-8") as f:
        dataset_papers = json.load(f)

    for p in dataset_papers:
        if p.get("year"):
            years.append(p["year"])
        if p.get("title"):
            titles.append(p["title"])

year_span = f"{min(years)}–{max(years)}" if years else "recent years"

titles_context = "; ".join(titles[:4]) or "recent Instagram analytics studies"

results_prompt = f"""
Write the Results section of a literature review on {topic}.

Studies reviewed ({year_span}):
{titles_context}

Summarize performance trends, improvements, and comparisons.
"""

results = generate_text(
    results_prompt,
    max_new_tokens=140
)

with open(f"{OUTPUT_DIR}/results.txt", "w", encoding="utf-8") as f:
    f.write(results.strip())

print("✅ Results generated")

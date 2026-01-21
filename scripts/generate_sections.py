import os
import re

INPUT_DIR = "data/generated"
OUTPUT_DIR = "data/generated/final"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def simple_summarize(text, max_sentences=10):
    """
    Simple synthesis logic:
    - Cleans text
    - Splits into sentences
    - Removes very short / noisy sentences
    - Keeps top N sentences
    """
    text = re.sub(r"\s+", " ", text)
    sentences = re.split(r"\. ", text)

    clean_sentences = [
        s.strip() for s in sentences
        if len(s.strip()) > 40
    ]

    summary = ". ".join(clean_sentences[:max_sentences])
    if summary and not summary.endswith("."):
        summary += "."

    return summary


for file in os.listdir(INPUT_DIR):
    if not file.endswith(".txt"):
        continue

    input_path = os.path.join(INPUT_DIR, file)

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 🔹 ACTUAL SYNTHESIS (Milestone-3 requirement)
    synthesized_text = simple_summarize(content)

    unified_text = (
        "SYNTHESIZED SECTION\n"
        "===================\n\n"
        f"{synthesized_text}"
    )

    output_path = os.path.join(OUTPUT_DIR, file)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(unified_text)

    print(f"Generated synthesized section: {file}")

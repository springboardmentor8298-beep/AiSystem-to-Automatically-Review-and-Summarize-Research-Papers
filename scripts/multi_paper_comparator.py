import os
import json
import re
from collections import Counter

SUMMARY_DIR = "outputs/section_summaries"
OUTPUT_FILE = "outputs/multi_paper_common_themes.json"

def tokenize(text):
    return re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())

def extract_keywords(section_summaries):
    keywords = Counter()
    for content in section_summaries.values():
        words = tokenize(content)
        keywords.update(words)
    return keywords

def main():
    global_keywords = Counter()

    for file in os.listdir(SUMMARY_DIR):
        if file.endswith("_section_summary.json"):
            print(f"Analyzing {file}")

            with open(os.path.join(SUMMARY_DIR, file), "r", encoding="utf-8") as f:
                summaries = json.load(f)

            paper_keywords = extract_keywords(summaries)
            global_keywords.update(paper_keywords)

    common_themes = global_keywords.most_common(20)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(common_themes, f, indent=2)

    print("Common research themes saved to:", OUTPUT_FILE)

if __name__ == "__main__":
    main()

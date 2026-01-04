import os
import re
import json

TEXT_DIR = "data/text"
OUTPUT_DIR = "outputs/sections"

os.makedirs(OUTPUT_DIR, exist_ok=True)

SECTION_PATTERNS = {
    "abstract": r"\babstract\b",
    "introduction": r"\bintroduction\b",
    "methods": r"\b(methods?|methodology)\b",
    "results": r"\b(results?|experiments?)\b",
    "discussion": r"\bdiscussion\b",
    "conclusion": r"\b(conclusion|conclusions)\b",
}

def parse_sections(text):
    sections = {}
    lower_text = text.lower()

    matches = []
    for section, pattern in SECTION_PATTERNS.items():
        match = re.search(pattern, lower_text)
        if match:
            matches.append((match.start(), section))

    matches.sort()

    for i, (start, section) in enumerate(matches):
        end = matches[i + 1][0] if i + 1 < len(matches) else len(text)
        sections[section] = text[start:end].strip()

    return sections

if __name__ == "__main__":
    for filename in os.listdir(TEXT_DIR):
        if filename.endswith(".txt"):
            print(f"Parsing sections from {filename}")

            with open(os.path.join(TEXT_DIR, filename), "r", encoding="utf-8") as f:
                text = f.read()

            parsed = parse_sections(text)

            output_file = filename.replace(".txt", "_sections.json")
            output_path = os.path.join(OUTPUT_DIR, output_file)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2)

            print(f"Saved sectioned text to: {output_path}")

import os
import json
import re

TEXT_DIR = "data/extracted_text"
SECTION_DIR = "data/sections"

os.makedirs(SECTION_DIR, exist_ok=True)

HEADERS = ["abstract", "introduction", "method", "results", "conclusion"]


def extract_sections():
    for file in os.listdir(TEXT_DIR):
        if not file.endswith(".txt"):
            continue

        input_path = os.path.join(TEXT_DIR, file)

        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read().lower()

        sections = {}

        # Find all header positions
        matches = []
        for header in HEADERS:
            match = re.search(rf"\b{header}\b", text)
            if match:
                matches.append((header, match.start()))

        # Sort headers by position in text
        matches.sort(key=lambda x: x[1])

        # Extract text between headers
        for i in range(len(matches)):
            header, start = matches[i]
            end = matches[i + 1][1] if i + 1 < len(matches) else len(text)
            section_text = text[start:end].strip()
            sections[header] = section_text

        # Save as JSON
        output_path = os.path.join(
            SECTION_DIR, file.replace(".txt", ".json")
        )
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(sections, f, indent=2)

        print(f"Sections extracted: {file}")


if __name__ == "__main__":
    extract_sections()

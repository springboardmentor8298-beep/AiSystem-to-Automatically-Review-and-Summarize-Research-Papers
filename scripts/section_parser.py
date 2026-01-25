import os
import re
import json

# ---------------------------------------
# DIRECTORIES
# ---------------------------------------
TEXT_DIR = "data/text"
OUTPUT_DIR = "outputs/sections"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------
# SECTION HEADERS (ROBUST PATTERNS)
# ---------------------------------------
SECTION_PATTERNS = {
    "abstract": r"\babstract\b",
    "introduction": r"\bintroduction\b",
    "methods": r"\b(methods?|methodology)\b",
    "results": r"\b(results?|experiments?)\b",
    "discussion": r"\bdiscussion\b",
    "conclusion": r"\b(conclusion|conclusions)\b",
}

# ---------------------------------------
# CLEANING FUNCTION (CRITICAL)
# ---------------------------------------
def clean_section(text: str) -> str:
    """
    Cleans noisy PDF artifacts:
    - URLs
    - Figure/Table captions
    - Reference leakage
    - Broken spacing
    """

    if not text:
        return ""

    # Remove URLs
    text = re.sub(r"http\S+", "", text)

    # Remove figure/table captions
    text = re.sub(
        r"\b(fig(ure)?|table)\s*\d+.*",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove references section if it leaks
    text = re.split(r"\breferences\b", text, flags=re.IGNORECASE)[0]

    # Remove excessive whitespace
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()

# ---------------------------------------
# SECTION PARSER
# ---------------------------------------
def parse_sections(text: str) -> dict:
    """
    Splits full paper text into clean semantic sections.
    """

    sections = {}
    lower_text = text.lower()

    matches = []

    for section, pattern in SECTION_PATTERNS.items():
        match = re.search(pattern, lower_text)
        if match:
            matches.append((match.start(), section))

    if not matches:
        return sections

    matches.sort()

    for i, (start, section) in enumerate(matches):
        end = matches[i + 1][0] if i + 1 < len(matches) else len(text)

        raw_section = text[start:end].strip()
        cleaned = clean_section(raw_section)

        if cleaned:
            sections[section] = cleaned

    return sections

# ---------------------------------------
# CLI TEST MODE
# ---------------------------------------
if __name__ == "__main__":

    for filename in os.listdir(TEXT_DIR):
        if not filename.endswith(".txt"):
            continue

        print(f"🔍 Parsing sections from: {filename}")

        file_path = os.path.join(TEXT_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        parsed_sections = parse_sections(text)

        if not parsed_sections:
            print("⚠️ No sections detected")
            continue

        output_file = filename.replace(".txt", "_sections.json")
        output_path = os.path.join(OUTPUT_DIR, output_file)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(parsed_sections, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved cleaned sections to: {output_path}")

import re

def clean_text_for_summary(text: str) -> str:
    cleaned_lines = []

    for line in text.splitlines():
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Remove table-like numeric noise
        if re.search(r"\b\d+\s+\d+\s+\d+\b", line):
            continue

        # Remove figure/table captions
        if line.lower().startswith(("figure", "table")):
            continue

        # Remove token grids / math-heavy lines
        if len(re.findall(r"\d", line)) > len(line) * 0.3:
            continue

        # Remove lines without spaces (PDF token garbage)
        if " " not in line:
            continue

        # Remove very short lines
        if len(line) < 40:
            continue

        cleaned_lines.append(line)

    return " ".join(cleaned_lines)

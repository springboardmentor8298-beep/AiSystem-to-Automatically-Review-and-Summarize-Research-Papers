import json
import os

OUTPUT_FILE = "app/output/combined_abstracts.json"


def clean_unicode(text: str) -> str:
    """
    Cleans common Unicode characters produced by LLMs
    to avoid Windows encoding issues.
    """
    if not text:
        return ""

    return (
        text.replace("“", '"')
            .replace("”", '"')
            .replace("’", "'")
            .replace("–", "-")
            .replace("—", "-")
            .replace("\u00a0", " ")
    )


def generate_draft():
    """
    Generates a structured research draft displaying
    title, authors, year, and AI-generated summary.
    """

    if not os.path.exists(OUTPUT_FILE):
        raise FileNotFoundError(
            "❌ combined_abstracts.json not found. "
            "Please run analysis step first."
        )

    # Read combined summaries
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    draft = []
    draft.append("## 📘 AI Research Paper Summary\n")

    for idx, item in enumerate(data, start=1):
        title = item.get("title", f"Paper {idx}")
        authors = ", ".join(item.get("authors", [])) or "Unknown"
        year = item.get("year", "N/A")
        summary = clean_unicode(item.get("summary", ""))

        # ✅ Change 4: Display metadata clearly
        draft.append(f"### 📄 {title}")
        draft.append(f"**Authors:** {authors}")
        draft.append(f"**Year:** {year}\n")
        draft.append(summary)
        draft.append("\n---\n")

    return "\n".join(draft)
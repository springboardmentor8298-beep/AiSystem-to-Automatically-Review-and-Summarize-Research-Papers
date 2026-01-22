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
    Generates a professional research draft with:
    - Paper Title
    - Authors
    - Year
    - AI-generated summary

    Output is clean text (no markdown symbols)
    suitable for UI display and reports.
    """

    if not os.path.exists(OUTPUT_FILE):
        raise FileNotFoundError(
            "❌ combined_abstracts.json not found. "
            "Please run analysis step first."
        )

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    draft_sections = []

    # Main heading
    draft_sections.append("AI Research Paper Summary\n")
    draft_sections.append("=" * 30 + "\n")

    for idx, item in enumerate(data, start=1):
        title = item.get("title", f"Research Paper {idx}")
        authors = ", ".join(item.get("authors", [])) or "Unknown Authors"
        year = item.get("year", "N/A")
        summary = clean_unicode(item.get("summary", ""))

        draft_sections.append(f"Paper {idx}")
        draft_sections.append("-" * 10)
        draft_sections.append(f"Title   : {title}")
        draft_sections.append(f"Authors : {authors}")
        draft_sections.append(f"Year    : {year}\n")
        draft_sections.append("Summary:")
        draft_sections.append(summary)
        draft_sections.append("\n" + "=" * 50 + "\n")

    return "\n".join(draft_sections)
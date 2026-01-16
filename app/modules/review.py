import os


def clean_unicode(text: str) -> str:
    """
    Cleans Unicode characters that cause Windows charmap errors.
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


def review_draft(draft: str) -> str:
    """
    Reviews and refines the generated draft.
    - Normalizes headings
    - Cleans encoding issues
    - Saves final reviewed draft
    """

    if not draft:
        raise ValueError("❌ Empty draft received for review")

    reviewed = draft.replace("###", "##")
    reviewed = clean_unicode(reviewed)

    output_path = "app/output/reviewed_research_draft.txt"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # ✅ Explicit UTF-8 encoding (IMPORTANT)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(reviewed)

    print(f"✅ Reviewed draft saved → {output_path}")

    return reviewed
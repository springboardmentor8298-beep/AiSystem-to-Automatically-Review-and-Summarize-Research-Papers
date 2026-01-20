import json
import os

DRAFT_PATH = "outputs/review_draft/review_draft.json"
FINAL_DIR = "outputs/final_review"
os.makedirs(FINAL_DIR, exist_ok=True)

def generate_markdown(review_draft):
    lines = []

    # Title
    lines.append(f"# {review_draft['title']}\n")

    # Sections
    for section in review_draft["sections"]:
        lines.append(f"## {section['section']}\n")
        lines.append(section["content"])
        lines.append("\n")

    return "\n".join(lines)

if __name__ == "__main__":
    with open(DRAFT_PATH, "r", encoding="utf-8") as f:
        review_draft = json.load(f)

    markdown_text = generate_markdown(review_draft)

    output_path = os.path.join(FINAL_DIR, "automated_review.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_text)

    print("Final review document generated at:", output_path)

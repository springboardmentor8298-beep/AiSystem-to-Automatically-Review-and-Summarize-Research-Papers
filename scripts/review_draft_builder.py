import json
import os

OUTLINE_PATH = "outputs/review_outline/review_outline.json"
SECTION_SUMMARY_DIR = "outputs/section_summaries"
DRAFT_DIR = "outputs/review_draft"
os.makedirs(DRAFT_DIR, exist_ok=True)

def load_outline():
    with open(OUTLINE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_section_summaries():
    summaries = []
    for file in os.listdir(SECTION_SUMMARY_DIR):
        if file.endswith(".json"):
            with open(os.path.join(SECTION_SUMMARY_DIR, file), "r", encoding="utf-8") as f:
                summaries.append(json.load(f))
    return summaries

def build_review_draft(outline, section_summaries):
    draft = {
        "title": outline["title"],
        "sections": []
    }

    for section in outline["sections"]:
        content_blocks = []
        for paper in section_summaries:
            for sec_name, summary in paper.items():
                content_blocks.append(summary)

        draft["sections"].append({
            "section": section["name"],
            "content": "\n\n".join(content_blocks)
        })

    return draft

if __name__ == "__main__":
    outline = load_outline()
    section_summaries = load_section_summaries()

    review_draft = build_review_draft(outline, section_summaries)

    output_path = os.path.join(DRAFT_DIR, "review_draft.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(review_draft, f, indent=4)

    print("Review draft generated at:", output_path)

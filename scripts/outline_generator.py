import json
import os

OUTPUT_DIR = "outputs"
OUTLINE_DIR = os.path.join(OUTPUT_DIR, "review_outline")
os.makedirs(OUTLINE_DIR, exist_ok=True)

def generate_outline(topic="Research Paper Review"):
    outline = {
        "title": f"Automated Review of {topic}",
        "sections": [
            {
                "id": 1,
                "name": "Introduction",
                "description": "Overview of the research problem and motivation."
            },
            {
                "id": 2,
                "name": "Background and Related Work",
                "description": "Summary of existing research and foundational concepts."
            },
            {
                "id": 3,
                "name": "Methodologies",
                "description": "Discussion of methods and approaches used in the papers."
            },
            {
                "id": 4,
                "name": "Comparative Analysis",
                "description": "Comparison of techniques, strengths, and limitations."
            },
            {
                "id": 5,
                "name": "Conclusion and Future Work",
                "description": "Overall findings and possible future research directions."
            }
        ]
    }
    return outline

if __name__ == "__main__":
    topic = "Attention Mechanisms in Deep Learning"
    outline = generate_outline(topic)

    output_path = os.path.join(OUTLINE_DIR, "review_outline.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(outline, f, indent=4)

    print("Review outline generated at:", output_path)

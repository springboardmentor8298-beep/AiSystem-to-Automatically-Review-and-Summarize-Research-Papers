import os
import sys

# Get topic from command-line argument
topic = sys.argv[1].strip().replace(" ", "_").lower()

BASE_DIR = f"generated_review/{topic}"
OUTPUT_FILE = f"{BASE_DIR}/final_report.txt"

sections = {
    "Abstract": "abstract.txt",
    "Methods": "methods.txt",
    "Results": "results.txt",
    "References": "references.txt"
}

os.makedirs(BASE_DIR, exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    out.write(f"Literature Review on {topic.replace('_', ' ').title()}\n")
    out.write("=" * 60 + "\n")

    for section_title, filename in sections.items():
        path = os.path.join(BASE_DIR, filename)

        out.write(f"\n\n{section_title}\n")
        out.write("-" * len(section_title) + "\n")

        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                out.write(f.read())
        else:
            out.write("[Section not available]\n")

print("✅ Final report generated successfully")

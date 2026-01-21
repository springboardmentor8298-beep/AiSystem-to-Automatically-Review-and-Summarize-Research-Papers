import os

INPUT_DIR = "data/generated/final"
OUTPUT_DIR = "data/generated/refined"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for file in os.listdir(INPUT_DIR):
    if not file.endswith(".txt"):
        continue

    with open(os.path.join(INPUT_DIR, file), "r", encoding="utf-8") as f:
        text = f.read()

    refined_text = (
        "REFINED VERSION\n"
        "================\n\n"
        + text.replace("SYNTHESIZED", "REFINED")
    )

    with open(os.path.join(OUTPUT_DIR, file), "w", encoding="utf-8") as f:
        f.write(refined_text)

    print(f"Refined section: {file}")

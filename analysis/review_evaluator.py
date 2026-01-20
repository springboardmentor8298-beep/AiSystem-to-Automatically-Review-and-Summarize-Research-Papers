import os

topic = input("Enter topic name: ").strip().replace(" ", "_").lower()
BASE_DIR = f"generated_review/{topic}"

sections = ["abstract.txt", "methods.txt", "results.txt", "references.txt"]

print("\n📊 Quality Evaluation Report\n")

for section in sections:
    path = f"{BASE_DIR}/{section}"

    if not os.path.exists(path):
        print(f"{section}: ❌ Missing")
        continue

    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if len(content) < 100:
        print(f"{section}: ⚠ Needs expansion")
    else:
        print(f"{section}: ✅ Good quality")

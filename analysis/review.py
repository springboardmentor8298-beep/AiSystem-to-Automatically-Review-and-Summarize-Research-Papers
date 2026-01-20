import json

def review_section(text, keywords):
    feedback = []

    if not text or len(text.split()) < 80:
        feedback.append("Section is too short and needs expansion.")

    missing = [k for k in keywords if k.lower() not in text.lower()]
    if missing:
        feedback.append(f"Missing important keywords: {', '.join(missing[:5])}")

    if not feedback:
        feedback.append("Section quality is good.")

    return feedback


def run_review():
    with open("analysis/keywords.json", "r", encoding="utf-8") as f:
        keywords = json.load(f)

    sections = {
        "Abstract": "generation/abstract.txt",
        "Methods": "generation/methods.txt",
        "Results": "generation/results.txt"
    }

    report = {}

    for name, path in sections.items():
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            report[name] = review_section(text, keywords)
        except FileNotFoundError:
            report[name] = ["Section file not found"]

    with open("analysis/review_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    return report


if __name__ == "__main__":
    print(run_review())

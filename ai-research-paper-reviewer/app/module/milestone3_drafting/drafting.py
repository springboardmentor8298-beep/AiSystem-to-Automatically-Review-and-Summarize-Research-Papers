import os
import json
from transformers import pipeline

# =========================
# CONFIG
# =========================
EXTRACTED_DIR = "extracted_data"
SECTION_FILE = "section_wise_text.json"
FINDINGS_FILE = "key_findings.json"

OUTPUT_DIR = "draft_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODEL_NAME = "google/flan-t5-base"

# =========================
# LOAD DATA
# =========================
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

sections = load_json(os.path.join(EXTRACTED_DIR, SECTION_FILE))
findings = load_json(os.path.join(EXTRACTED_DIR, FINDINGS_FILE))

# =========================
# LOAD MODEL
# =========================
print("[INFO] Loading Hugging Face model...")
generator = pipeline(
    "text2text-generation",
    model=MODEL_NAME,
    max_length=512
)

# =========================
# SYNTHESIS
# =========================
def synthesize_findings(findings_dict):
    merged = []
    for paper, points in findings_dict.items():
        merged.extend(points)
    return "\n".join(set(merged))

# =========================
# DRAFT GENERATORS
# =========================
def generate_abstract(synthesized):
    prompt = f"""
Write an academic abstract based on the following research findings:

{synthesized}
"""
    return generator(prompt)[0]["generated_text"]

def generate_methods(sections_dict):
    methods_text = "\n".join(
        sec["methodology"] for sec in sections_dict.values()
        if sec.get("methodology")
    )

    prompt = f"""
Write a unified Methods section using the following methodology descriptions:

{methods_text}
"""
    return generator(prompt)[0]["generated_text"]

def generate_results(synthesized):
    prompt = f"""
Write a structured Results section comparing findings across studies:

{synthesized}
"""
    return generator(prompt)[0]["generated_text"]

# =========================
# APA REFERENCES (RULE-BASED)
# =========================
def generate_apa_references(sections_dict):
    references = []
    for paper in sections_dict.keys():
        title = paper.replace("_", " ").replace(".pdf", "")
        ref = f"{title}. (2024). Retrieved from Semantic Scholar."
        references.append(ref)
    return references

# =========================
# PIPELINE
# =========================
def run_milestone_3():
    print("[INFO] Synthesizing findings...")
    synthesized = synthesize_findings(findings)

    print("[INFO] Generating Abstract...")
    abstract = generate_abstract(synthesized)

    print("[INFO] Generating Methods...")
    methods = generate_methods(sections)

    print("[INFO] Generating Results...")
    results = generate_results(synthesized)

    print("[INFO] Generating APA References...")
    references = generate_apa_references(sections)

    final_draft = {
        "abstract": abstract,
        "methods": methods,
        "results": results,
        "references": references
    }

    # Save JSON
    with open(os.path.join(OUTPUT_DIR, "final_draft.json"), "w", encoding="utf-8") as f:
        json.dump(final_draft, f, indent=2)

    # Save readable text
    with open(os.path.join(OUTPUT_DIR, "final_draft.txt"), "w", encoding="utf-8") as f:
        f.write("ABSTRACT\n" + abstract + "\n\n")
        f.write("METHODS\n" + methods + "\n\n")
        f.write("RESULTS\n" + results + "\n\n")
        f.write("REFERENCES\n")
        for r in references:
            f.write("- " + r + "\n")

    print("\n[SUCCESS] Milestone 3 completed")
    print("[OUTPUT] Draft saved in draft_output/")

# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    run_milestone_3()

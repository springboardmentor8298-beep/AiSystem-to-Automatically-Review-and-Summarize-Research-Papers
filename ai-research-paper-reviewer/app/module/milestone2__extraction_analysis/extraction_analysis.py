import os
import json
import fitz  # PyMuPDF

# =========================
# CONFIG
# =========================
PDF_DIR = "papers"
OUTPUT_DIR = "extracted_data"
SECTION_FILE = "section_wise_text.json"
KEY_FILE = "key_findings.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# PDF TEXT EXTRACTION
# =========================
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text()

    return text.strip()

# =========================
# SECTION SPLITTING (RULE BASED)
# =========================
def split_into_sections(text):
    sections = {
        "introduction": "",
        "methodology": "",
        "results": "",
        "conclusion": ""
    }

    lower_text = text.lower()

    def get_section(start_keywords, end_keywords):
        for start in start_keywords:
            if start in lower_text:
                start_idx = lower_text.find(start)
                for end in end_keywords:
                    end_idx = lower_text.find(end, start_idx + 50)
                    if end_idx != -1:
                        return text[start_idx:end_idx]
        return ""

    sections["introduction"] = get_section(
        ["introduction"],
        ["method", "methodology"]
    )

    sections["methodology"] = get_section(
        ["method", "methodology"],
        ["result", "results"]
    )

    sections["results"] = get_section(
        ["result", "results"],
        ["conclusion", "discussion"]
    )

    sections["conclusion"] = get_section(
        ["conclusion", "discussion"],
        []
    )

    return sections

# =========================
# KEY FINDINGS EXTRACTION
# =========================
def extract_key_findings(results_text):
    findings = []
    sentences = results_text.split(".")

    for sentence in sentences:
        s = sentence.strip()
        if any(word in s.lower() for word in ["improve", "increase", "outperform", "better", "significant"]):
            findings.append(s)

    return findings[:5]  # keep it tight

# =========================
# PIPELINE
# =========================
def run_milestone_2():
    section_dataset = {}
    key_findings_dataset = {}

    pdf_files = [f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]

    if not pdf_files:
        raise RuntimeError("No PDFs found. Run Milestone 1 first.")

    for pdf in pdf_files:
        print(f"[PROCESSING] {pdf}")
        path = os.path.join(PDF_DIR, pdf)

        raw_text = extract_text_from_pdf(path)
        if len(raw_text) < 500:
            print(f"[WARNING] Low text extracted from {pdf}")

        sections = split_into_sections(raw_text)
        findings = extract_key_findings(sections.get("results", ""))

        section_dataset[pdf] = sections
        key_findings_dataset[pdf] = findings

    # Save outputs
    with open(os.path.join(OUTPUT_DIR, SECTION_FILE), "w", encoding="utf-8") as f:
        json.dump(section_dataset, f, indent=2)

    with open(os.path.join(OUTPUT_DIR, KEY_FILE), "w", encoding="utf-8") as f:
        json.dump(key_findings_dataset, f, indent=2)

    print("\n[SUCCESS] Milestone 2 completed")
    print("[OUTPUT] Section-wise text + key findings saved")

# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    run_milestone_2()

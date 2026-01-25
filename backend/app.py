from flask import Flask, request, jsonify
from flask_cors import CORS
from spellchecker import SpellChecker
import os
import sys

# -----------------------------------------
# PATH FIX
# -----------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PROJECT_ROOT)

# -----------------------------------------
# IMPORTS
# -----------------------------------------
from scripts.search_and_list import search_semanticscholar
from scripts.summarization_pipeline import generate_summary
from scripts.download_and_extract import download_and_extract
from scripts.section_parser import parse_sections
from scripts.text_cleaner import clean_text_for_summary

# -----------------------------------------
# FLASK APP
# -----------------------------------------
app = Flask(__name__)
CORS(app)

spell = SpellChecker()
SUMMARY_CACHE = {}

# -----------------------------------------
# HEALTH CHECK
# -----------------------------------------
@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "API running",
        "endpoints": ["/search", "/summarize_abstract", "/summarize"]
    })

# -----------------------------------------
# SEARCH PAPERS (STRICT + MODE AWARE)
# -----------------------------------------
@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "").strip()
    limit = int(request.args.get("limit", 5))
    mode = request.args.get("mode", "abstract")  # abstract | full

    if not query:
        return jsonify({"error": "Query required"}), 400

    # Spell correction (safe)
    corrected_query = " ".join(
        spell.correction(word) or word
        for word in query.split()
    )

    print(f"[SEARCH] {query} → {corrected_query} | mode={mode}")

    raw_papers = search_semanticscholar(corrected_query, limit * 10)

    results = []
    abstracts_for_overall = []

    for p in raw_papers:
        if len(results) >= limit:
            break

        abstract = (p.get("abstract") or "").strip()
        pdf_url = p.get("openAccessPdf", {}).get("url")
        publisher_url = p.get("url")  # ALWAYS available

        # -------- HARD QUALITY FILTERS --------
        if not abstract:
            continue
        if len(abstract) < 300:
            continue
        if abstract.count(".") < 2:
            continue

        # -------- FULL MODE: REQUIRE PDF --------
        if mode == "full" and not pdf_url:
            continue

        abstracts_for_overall.append(abstract)

        results.append({
            "title": p.get("title"),
            "year": p.get("year"),
            "venue": p.get("venue"),
            "abstract": abstract,
            "pdf_url": pdf_url,
            "publisher_url": publisher_url
        })

    # -------- OVERALL TOPIC SUMMARY --------
    overall_summary = ""
    if abstracts_for_overall:
        combined = " ".join(abstracts_for_overall[:5])
        overall_summary = generate_summary(
            clean_text_for_summary(combined)
        )

    return jsonify({
        "query": corrected_query,
        "original_query": query,
        "paper_count": len(results),
        "overall_summary": overall_summary,
        "papers": results
    })

# -----------------------------------------
# ABSTRACT SUMMARY
# -----------------------------------------
@app.route("/summarize_abstract", methods=["POST"])
def summarize_abstract():
    data = request.get_json(silent=True) or {}
    abstract = (data.get("abstract") or "").strip()

    if not abstract:
        return jsonify({"summary": ""})

    cleaned = clean_text_for_summary(abstract)
    return jsonify({"summary": generate_summary(cleaned)})

# -----------------------------------------
# FULL PAPER SUMMARY (SAFE & SECTION AWARE)
# -----------------------------------------
@app.route("/summarize", methods=["POST"])
def summarize_pdf():
    data = request.get_json(silent=True) or {}
    pdf_url = data.get("pdf_url")

    if not pdf_url:
        return jsonify({"error": "PDF URL missing"}), 400

    # Cache hit
    if pdf_url in SUMMARY_CACHE:
        return jsonify(SUMMARY_CACHE[pdf_url])

    # Download & extract (403-safe)
    raw_text = download_and_extract(pdf_url)

    # ❌ PDF exists but blocked / forbidden
    if not raw_text or not raw_text.strip():
        return jsonify({
            "error": "PDF not accessible for summarization"
        }), 400

    sections = parse_sections(raw_text)

    result = {
        "abstract": "",
        "introduction": "",
        "conclusion": ""
    }

    # Section-wise summaries (clean only)
    for key in ["abstract", "introduction", "conclusion"]:
        cleaned = clean_text_for_summary(sections.get(key, ""))
        if len(cleaned) >= 300:
            result[key] = generate_summary(cleaned)

    SUMMARY_CACHE[pdf_url] = result
    return jsonify(result)

# -----------------------------------------
# RUN
# -----------------------------------------
if __name__ == "__main__":
    app.run(debug=True)

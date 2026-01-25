from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# --------------------------------------------------
# PATH FIX
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# --------------------------------------------------
# IMPORTS
# --------------------------------------------------
from scripts.search_and_list import search_semanticscholar
from scripts.summarization_pipeline import generate_summary
from scripts.download_and_extract import download_and_extract
from scripts.section_parser import parse_sections
from scripts.text_cleaner import clean_text_for_summary

# --------------------------------------------------
# FLASK APP
# --------------------------------------------------
app = Flask(__name__)
CORS(app)

# --------------------------------------------------
# IN-MEMORY CACHE (PREVENT API OVERUSE)
# --------------------------------------------------
SUMMARY_CACHE = {}

# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------
@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "API running",
        "message": "Use /search, /summarize_abstract, /summarize"
    })

# --------------------------------------------------
# SEARCH PAPERS (SAFE, NO OFFSET, LIMIT GUARANTEED)
# --------------------------------------------------
@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "").strip()
    limit = int(request.args.get("limit", 5))

    if not query:
        return jsonify({"error": "Query is required"}), 400

    # Fetch extra papers, filter locally
    raw_papers = search_semanticscholar(query, limit * 4)

    accessible_papers = []
    abstracts_for_summary = []

    for p in raw_papers:
        if len(accessible_papers) >= limit:
            break

        pdf_url = None
        if isinstance(p.get("openAccessPdf"), dict):
            pdf_url = p["openAccessPdf"].get("url")

        abstract = (p.get("abstract") or "").strip()
        publisher_url = p.get("url")

        # Skip papers with no usable content
        if not abstract and not pdf_url:
            continue

        if abstract:
            abstracts_for_summary.append(abstract)

        accessible_papers.append({
            "title": p.get("title"),
            "year": p.get("year"),
            "venue": p.get("venue"),
            "abstract": abstract,
            "pdf_url": pdf_url,
            "publisher_url": publisher_url
        })

    # --------------------------------------------------
    # OVERALL SUMMARY (ABSTRACTS ONLY)
    # --------------------------------------------------
    overall_summary = ""
    if abstracts_for_summary:
        combined = " ".join(abstracts_for_summary[:5])
        overall_summary = generate_summary(combined)

    return jsonify({
        "query": query,
        "paper_count": len(accessible_papers),
        "overall_summary": overall_summary,
        "papers": accessible_papers
    })

# --------------------------------------------------
# ABSTRACT SUMMARY
# --------------------------------------------------
@app.route("/summarize_abstract", methods=["POST", "OPTIONS"])
def summarize_abstract():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.get_json(silent=True) or {}
    abstract = (data.get("abstract") or "").strip()

    if not abstract:
        return jsonify({"summary": "No abstract available."})

    summary = generate_summary(abstract)
    return jsonify({"summary": summary})

# --------------------------------------------------
# FULL PAPER SUMMARY (SECTION AWARE + CACHED)
# --------------------------------------------------
@app.route("/summarize", methods=["POST", "OPTIONS"])
def summarize_pdf():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.get_json(silent=True) or {}
    pdf_url = data.get("pdf_url")

    if not pdf_url:
        return jsonify({"error": "No PDF URL provided."}), 400

    # 🔥 CACHE HIT
    if pdf_url in SUMMARY_CACHE:
        return jsonify(SUMMARY_CACHE[pdf_url])

    try:
        # 1️⃣ Download & extract
        raw_text = download_and_extract(pdf_url)
        if not raw_text.strip():
            return jsonify({"error": "No text extracted from PDF."}), 400

        # 2️⃣ Parse sections
        sections = parse_sections(raw_text)

        # 3️⃣ Always return consistent keys
        result = {
            "abstract": "Not available.",
            "introduction": "Not available.",
            "conclusion": "Not available.",
            "full": "Not available."
        }

        # 4️⃣ Section-wise summaries
        for key in ["abstract", "introduction", "conclusion"]:
            if key in sections:
                cleaned = clean_text_for_summary(sections[key])
                if cleaned.strip():
                    result[key] = generate_summary(cleaned)

        # 5️⃣ Full summary (merged important sections)
        merged = ""
        for key in ["abstract", "introduction", "conclusion"]:
            if key in sections:
                merged += sections[key] + "\n\n"

        if not merged.strip():
            merged = raw_text[:8000]

        cleaned_full = clean_text_for_summary(merged)
        if cleaned_full.strip():
            result["full"] = generate_summary(cleaned_full)

        # 🔐 SAVE TO CACHE
        SUMMARY_CACHE[pdf_url] = result

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --------------------------------------------------
# RUN
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)

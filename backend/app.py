from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# --------------------------------------------------
# PATH FIX (so scripts/ imports always work)
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# --------------------------------------------------
# IMPORT PIPELINE
# --------------------------------------------------
from scripts.search_and_list import search_semanticscholar
from scripts.summarization_pipeline import generate_summary
from scripts.download_and_extract import download_and_extract

# --------------------------------------------------
# FLASK APP
# --------------------------------------------------
app = Flask(__name__)

# 🔥 THIS IS CRITICAL (allow all origins + preflight)
CORS(app, supports_credentials=True)

# --------------------------------------------------
# ROUTES
# --------------------------------------------------

@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "API running",
        "message": "Use /search, /summarize_abstract, /summarize"
    })


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "")
    limit = int(request.args.get("limit", 5))

    results = search_semanticscholar(query, limit)
    return jsonify({"data": results})


@app.route("/summarize_abstract", methods=["POST", "OPTIONS"])
def summarize_abstract():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.get_json()
    abstract = data.get("abstract", "")

    if not abstract.strip():
        return jsonify({"summary": "No abstract available."})

    summary = generate_summary(abstract)
    return jsonify({"summary": summary})


@app.route("/summarize", methods=["POST", "OPTIONS"])
def summarize_pdf():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.get_json()
    pdf_url = data.get("pdf_url")

    if not pdf_url:
        return jsonify({"summary": "No PDF URL provided."})

    try:
        text = download_and_extract(pdf_url)
        summary = generate_summary(text)
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"summary": f"PDF summarization failed: {e}"})


# --------------------------------------------------
# RUN
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)

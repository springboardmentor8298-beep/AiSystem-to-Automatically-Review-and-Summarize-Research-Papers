from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read API key from environment
API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

if not API_KEY:
    raise RuntimeError("Semantic Scholar API key not found. Check your .env file.")

app = Flask(__name__)
CORS(app)

SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/search"

def search_papers(query, limit):
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,year,abstract,url,openAccessPdf"
    }

    headers = {
        "x-api-key": API_KEY
    }

    for attempt in range(5):
        response = requests.get(
            SEMANTIC_SCHOLAR_API,
            params=params,
            headers=headers
        )

        if response.status_code == 200:
            return response.json().get("data", [])
        elif response.status_code == 429:
            time.sleep(2 ** attempt)
        else:
            response.raise_for_status()

    return []

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")
    limit = request.args.get("limit", default=5, type=int)

    if not query:
        return jsonify({"error": "Query is required"}), 400

    results = search_papers(query, limit)
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)

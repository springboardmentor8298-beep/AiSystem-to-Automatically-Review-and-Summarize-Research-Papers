# scripts/search_and_list.py
"""
Improved Semantic Scholar search with better headers, safer fields, clearer error output,
and exponential backoff tuned for public API usage.
"""
import argparse
import json
import time
import urllib.parse
import os
from pathlib import Path
import requests

API_BASE = "https://api.semanticscholar.org/graph/v1/paper/search"
# use a smaller set of widely-supported fields to avoid "400 Bad Request"
DEFAULT_FIELDS = "title,authors,year,abstract,externalIds,url,venue"

# Read API key from env var if provided (recommended)
API_KEY = os.environ.get("S2_API_KEY")  # set this in your system if you have a key

def backoff_sleep(attempt):
    # slightly randomized exponential backoff
    wait = min(60, (2 ** attempt) + (attempt * 0.5))
    time.sleep(wait)

def search_semanticscholar(query, limit=10, fields=DEFAULT_FIELDS, retries=6):
    results = []
    offset = 0
    per_call = min(limit, 100)
    fetched = 0
    attempt = 0

    headers = {
        "User-Agent": "paper-summarizer/1.0 (+https://your-project.example)",
        "Accept": "application/json",
    }
    if API_KEY:
        headers["x-api-key"] = API_KEY

    while fetched < limit:
        params = {
            "query": query,
            "limit": per_call,
            "offset": offset,
            "fields": fields,
        }
        url = API_BASE + "?" + urllib.parse.urlencode(params)
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                batch = data.get("data", []) or data.get("results", [])
                if not batch:
                    break
                results.extend(batch)
                fetched += len(batch)
                offset += len(batch)
                attempt = 0
            elif resp.status_code == 429:
                # rate limited: backoff then retry
                print("Rate limited by API (429). Backing off...")
                backoff_sleep(attempt)
                attempt += 1
                if attempt > retries:
                    raise RuntimeError("Max retries exceeded (rate limit).")
                continue
            elif resp.status_code == 400:
                # bad request - show server message for debugging
                try:
                    print("400 Bad Request response body:", resp.json())
                except Exception:
                    print("400 Bad Request raw body:", resp.text[:1000])
                raise RuntimeError("400 Bad Request from Semantic Scholar API.")
            else:
                # raise for other HTTP errors (401, 403, 500 etc.)
                resp.raise_for_status()
        except requests.RequestException as e:
            print("Request failed:", e)
            backoff_sleep(attempt)
            attempt += 1
            if attempt > retries:
                raise
            continue

    return results[:limit]

def save_results(query, results, out_dir="outputs"):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_query = "".join(c if c.isalnum() or c in "-_ " else "_" for c in query)[:80].strip().replace(" ", "_")
    out_file = out_dir / f"{safe_query}_metadata.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"query": query, "count": len(results), "results": results}, f, indent=2, ensure_ascii=False)
    return out_file

def print_summary(results, limit=10):
    print(f"\nTop {min(limit, len(results))} results:")
    for i, r in enumerate(results[:limit], start=1):
        title = r.get("title", "<no title>")
        year = r.get("year", "n/a")
        pdf = None
        oap = r.get("openAccessPdf")
        if oap and isinstance(oap, dict):
            pdf = oap.get("url")
        print(f"{i:2d}. {title[:160]} ({year})")
        if pdf:
            print(f"     PDF/Link: {pdf}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", "-q", required=True, help="Search query (topic)")
    parser.add_argument("--limit", "-n", type=int, default=10, help="Number of results to fetch")
    parser.add_argument("--out", "-o", default="outputs", help="Output folder")
    args = parser.parse_args()

    print("Searching Semantic Scholar for:", args.query)
    results = search_semanticscholar(args.query, limit=args.limit)
    if not results:
        print("No results found.")
        return

    out_file = save_results(args.query, results, out_dir=args.out)
    print(f"\nSaved metadata for {len(results)} papers to: {out_file}")
    print_summary(results, limit=args.limit)

if __name__ == "__main__":
    main()

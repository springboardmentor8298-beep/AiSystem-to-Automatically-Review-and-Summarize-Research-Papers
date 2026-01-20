"""
Improved Semantic Scholar search with:
- Safe exponential backoff
- No crashes on rate limits
- Works with or without API key
- UI-safe (always returns a list)
"""

import argparse
import json
import time
import urllib.parse
import os
from pathlib import Path
import requests

API_BASE = "https://api.semanticscholar.org/graph/v1/paper/search"

# Keep fields minimal to avoid 400 errors
DEFAULT_FIELDS = "title,year,abstract,openAccessPdf,url,venue"

# Optional API key
API_KEY = os.environ.get("S2_API_KEY")


# -----------------------------
# BACKOFF HELPER
# -----------------------------
def backoff_sleep(attempt):
    wait = min(60, (2 ** attempt))
    time.sleep(wait)


# -----------------------------
# SAFE SEARCH FUNCTION
# -----------------------------
def search_semanticscholar(query, limit=10, fields=DEFAULT_FIELDS, retries=6):
    results = []
    offset = 0
    per_call = min(limit, 100)
    fetched = 0
    attempt = 0

    headers = {
        "User-Agent": "paper-summarizer/1.0",
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

            # -------------------------
            # SUCCESS
            # -------------------------
            if resp.status_code == 200:
                data = resp.json()
                batch = data.get("data", []) or []

                if not batch:
                    break

                results.extend(batch)
                fetched += len(batch)
                offset += len(batch)
                attempt = 0
                continue

            # -------------------------
            # RATE LIMIT (SAFE HANDLING)
            # -------------------------
            if resp.status_code == 429:
                print("Rate limited by API (429). Backing off...")
                backoff_sleep(attempt)
                attempt += 1

                if attempt > retries:
                    print("Max retries exceeded. Returning partial/empty results.")
                    return results[:limit]

                continue

            # -------------------------
            # BAD REQUEST
            # -------------------------
            if resp.status_code == 400:
                print("400 Bad Request from Semantic Scholar.")
                return results[:limit]

            # -------------------------
            # OTHER ERRORS
            # -------------------------
            print(f"Semantic Scholar error: {resp.status_code}")
            return results[:limit]

        except requests.RequestException as e:
            print("Request exception:", e)
            backoff_sleep(attempt)
            attempt += 1

            if attempt > retries:
                print("Network retries exhausted. Returning results.")
                return results[:limit]

    return results[:limit]


# -----------------------------
# SAVE RESULTS
# -----------------------------
def save_results(query, results, out_dir="outputs"):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    safe_query = "".join(
        c if c.isalnum() or c in "-_ " else "_"
        for c in query
    ).strip().replace(" ", "_")[:80]

    out_file = out_dir / f"{safe_query}_metadata.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "query": query,
                "count": len(results),
                "results": results,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    return out_file


# -----------------------------
# PRINT SUMMARY (CLI)
# -----------------------------
def print_summary(results, limit=10):
    print(f"\nTop {min(limit, len(results))} results:")
    for i, r in enumerate(results[:limit], start=1):
        title = r.get("title", "<no title>")
        year = r.get("year", "n/a")
        pdf = None

        oap = r.get("openAccessPdf")
        if isinstance(oap, dict):
            pdf = oap.get("url")

        print(f"{i:2d}. {title[:160]} ({year})")
        if pdf:
            print(f"     PDF: {pdf}")


# -----------------------------
# CLI ENTRY
# -----------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", "-q", required=True, help="Search topic")
    parser.add_argument("--limit", "-n", type=int, default=10)
    parser.add_argument("--out", "-o", default="outputs")
    args = parser.parse_args()

    print("Searching Semantic Scholar for:", args.query)

    results = search_semanticscholar(args.query, limit=args.limit)

    if not results:
        print("No results found (or rate limited).")
        return

    out_file = save_results(args.query, results, out_dir=args.out)
    print(f"\nSaved {len(results)} results to: {out_file}")
    print_summary(results, limit=args.limit)


if __name__ == "__main__":
    main()

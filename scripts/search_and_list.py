import requests
import time
import json
import os
import argparse

API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "title,year,authors,abstract,url,citationCount,externalIds,openAccessPdf"

def search_semantic_scholar(query, limit, max_retries=3):
    params = {
        "query": query,
        "limit": limit,
        "fields": FIELDS
    }

    retries = 0
    while retries < max_retries:
        response = requests.get(API_URL, params=params)

        if response.status_code == 429:
            print("Rate limit hit… waiting 3s")
            time.sleep(3)
            retries += 1
            continue

        if response.status_code != 200:
            print(f"Error {response.status_code}… retrying")
            retries += 1
            time.sleep(2)
            continue

        data = response.json()
        papers = []

        for p in data.get("data", []):
            papers.append({
                "title": p.get("title"),
                "year": p.get("year"),
                "authors": [a["name"] for a in p.get("authors", [])],
                "abstract": p.get("abstract"),
                "url": p.get("url"),
                "citations": p.get("citationCount"),
                "externalIds": p.get("externalIds", {}),
                "openAccessPdf": p.get("openAccessPdf", {})
            })

        return papers

    print("Failed after retries")
    return []


def save_metadata(query, papers):
    os.makedirs("data/metadata", exist_ok=True)
    filename = query.replace(" ", "_")
    path = f"data/metadata/{filename}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2)

    print(f"Saved metadata: {path}")


def print_top_n(papers, n):
    print("\nTop Papers:\n")
    for i, p in enumerate(papers[:n], 1):
        print(f"{i}. {p['title']} ({p['year']})")
        print(f"   Authors: {', '.join(p['authors'])}")
        print(f"   Citations: {p['citations']}")
        print(f"   URL: {p['url']}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("topic")
    parser.add_argument("--n", type=int, default=5)
    args = parser.parse_args()

    papers = search_semantic_scholar(args.topic, args.n)

    if papers:
        save_metadata(args.topic, papers)
        print_top_n(papers, args.n)
    else:
        print("No results found.")

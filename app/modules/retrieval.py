import requests

SEMANTIC_API = "https://api.semanticscholar.org/graph/v1/paper/search"

def download_papers(topic, limit=5):
    params = {
        "query": topic,
        "limit": limit,
        "fields": "title,year,authors,openAccessPdf"
    }

    response = requests.get(SEMANTIC_API, params=params)
    data = response.json()

    papers = []

    for paper in data.get("data", []):
        pdf = paper.get("openAccessPdf")
        if pdf and pdf.get("url"):
            authors = [a.get("name") for a in paper.get("authors", [])]
            papers.append({
                "title": paper.get("title", "Unknown"),
                "year": paper.get("year", "N/A"),
                "authors": authors,
                "url": pdf["url"]
            })
        else:
            print("⏭ Skipping paywalled paper")

    print(f"📄 Retrieved {len(papers)} open-access papers")
    return papers
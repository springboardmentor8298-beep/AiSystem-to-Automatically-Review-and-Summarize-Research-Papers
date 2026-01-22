import requests
import time

SEMANTIC_API = "https://api.semanticscholar.org/graph/v1/paper/search"


def download_papers(topic: str, limit: int = 5):
    """
    Fetches open-access research papers using Semantic Scholar API.

    Fix:
    - Fetches more results than requested
    - Filters open-access PDFs
    - Stops only after collecting required number
    """

    if not topic.strip():
        return []

    collected_papers = []
    offset = 0
    batch_size = 10  # fetch more to compensate for filtering

    while len(collected_papers) < limit:
        params = {
            "query": topic,
            "limit": batch_size,
            "offset": offset,
            "fields": "title,year,authors,openAccessPdf"
        }

        try:
            response = requests.get(SEMANTIC_API, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"❌ Semantic Scholar API error: {e}")
            break

        papers = data.get("data", [])
        if not papers:
            break  # no more results

        for paper in papers:
            pdf_info = paper.get("openAccessPdf")

            if pdf_info and pdf_info.get("url"):
                authors = [
                    author.get("name", "Unknown Author")
                    for author in paper.get("authors", [])
                ]

                collected_papers.append({
                    "title": paper.get("title", "Unknown Title"),
                    "year": paper.get("year", "N/A"),
                    "authors": authors,
                    "url": pdf_info["url"]
                })

                if len(collected_papers) >= limit:
                    break

            time.sleep(0.1)

        offset += batch_size

    print(f"📄 Requested {limit}, Retrieved {len(collected_papers)} open-access papers")
    return collected_papers

import os
import json
import requests
import time
from dotenv import load_dotenv
from semanticscholar import SemanticScholar
import pymupdf4llm

load_dotenv()

S2_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
sch = SemanticScholar(api_key=S2_API_KEY) if S2_API_KEY else SemanticScholar()

PAPERS_FOLDER = "papers"
DATASET_FILE = "dataset.json"
os.makedirs(PAPERS_FOLDER, exist_ok=True)

MAX_SUCCESSFUL_PAPERS = 10  # As per your project (adjustable)

def collect_successful_papers(topic: str):
    print(f"\n🔍 Searching for: '{topic}'")
    print(f"   Goal: Find up to {MAX_SUCCESSFUL_PAPERS} papers with downloadable open-access PDFs\n")
    
    successful_papers = []
    fetched = 0
    batch_size = 50  # Larger batch to increase chance of finding open-access ones
    
    while len(successful_papers) < MAX_SUCCESSFUL_PAPERS:
        try:
            print(f"   Fetching {batch_size} papers (total fetched: {fetched})...")
            results = list(sch.search_paper(
                query=topic,
                limit=batch_size,
                fields=['title', 'authors', 'year', 'abstract', 'openAccessPdf', 'citationCount']
            ))
            
            if not results:
                print("   No more results available.\n")
                break
            
            fetched += len(results)
            
            for item in results:
                if len(successful_papers) >= MAX_SUCCESSFUL_PAPERS:
                    break
                
                pdf_url = item.openAccessPdf['url'] if item.openAccessPdf else None
                if not pdf_url:
                    continue  # Skip if no open-access PDF
                
                title = item.title
                print(f"   Trying: {title} ({item.year})")
                
                pdf_path = download_pdf(pdf_url, f"{len(successful_papers)+1}_{title}")
                if pdf_path:
                    sections = extract_sections(pdf_path)
                    
                    paper = {
                        "title": title,
                        "authors": [a['name'] for a in item.authors],
                        "year": item.year,
                        "abstract": item.abstract or "No abstract",
                        "citations": item.citationCount or 0,
                        "pdf_file": os.path.basename(pdf_path),
                        "sections": sections
                    }
                    successful_papers.append(paper)
                    print(f"  Added! ({len(successful_papers)}/{MAX_SUCCESSFUL_PAPERS})\n")
            
            time.sleep(2)  # Be gentle on API
            
        except Exception as e:
            print(f"   Temporary error: {e}. Waiting 10 seconds...\n")
            time.sleep(10)
    
    return successful_papers

def download_pdf(pdf_url: str, title_prefix: str) -> str | None:
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title_prefix)[:100]
    filename = f"{safe_title}.pdf"
    path = os.path.join(PAPERS_FOLDER, filename)
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(pdf_url, stream=True, timeout=120, headers=headers)
        if response.status_code == 200:
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return path
    except:
        pass
    return None

def extract_sections(pdf_path: str) -> dict:
    try:
        md_text = pymupdf4llm.to_markdown(pdf_path)
        sections = {}
        current = "Full Text"
        for line in md_text.split("\n"):
            stripped = line.strip()
            if stripped.startswith(("# ", "## ", "### ")):
                current = stripped.lstrip("# ").strip()
            elif stripped:
                sections.setdefault(current, "")
                sections[current] += stripped + " "
        for k in sections:
            sections[k] = sections[k].strip()
        return sections
    except:
        return {"error": "Failed to extract"}

if __name__ == "__main__":
    print(" AI Paper Reviewer  Smart Open-Access Collection (Max 10 Successful Papers)\n")
    
    topic = input("Enter research topic: ").strip()
    if not topic:
        topic = "attention is all you need"  # Best test topic
    
    papers = collect_successful_papers(topic)
    
    if not papers:
        print("Could not find any papers with downloadable PDFs. Try a different topic.")
    else:
        # Save dataset
        dataset_path = os.path.join(os.getcwd(), DATASET_FILE)
        with open(DATASET_FILE, "w", encoding="utf-8") as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
        
        print(f" SUCCESS!")
        print(f"   • Collected {len(papers)} high-quality papers with full text")
        print(f"   • PDFs saved in: {PAPERS_FOLDER}/")
        print(f"   • Dataset saved: {DATASET_FILE}")
        print("\nReady for Milestone 3: LLM Analysis & Draft Generation!")
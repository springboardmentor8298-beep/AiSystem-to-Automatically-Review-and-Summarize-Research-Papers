import os
import json
import streamlit as st
import requests
from semanticscholar import SemanticScholar
import pymupdf4llm
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Use your Semantic Scholar API key from .env (for higher rate limit)
S2_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
sch = SemanticScholar(api_key=S2_API_KEY) if S2_API_KEY else SemanticScholar()

# Folders & files
PAPERS_FOLDER = "papers"
DATASET_FILE = "dataset.json"
os.makedirs(PAPERS_FOLDER, exist_ok=True)

MAX_PAPERS = 10  # Adjustable (document allows up to 3–10)

# ========================
# Core Functions
# ========================
def search_and_collect_papers(topic: str):
    st.write(f"🔍 Research Phase: Searching Semantic Scholar for **{topic}**")
    st.write(f"Goal: Collect up to {MAX_PAPERS} papers with open-access PDFs")

    successful_papers = []
    batch_size = 50

    with st.spinner("Fetching papers..."):
        results = list(sch.search_paper(
            query=topic,
            limit=batch_size,
            fields=['title', 'authors', 'year', 'abstract', 'openAccessPdf', 'citationCount']
        ))

        if not results:
            st.error("No papers found. Try a different topic.")
            return []

        st.write(f"Found {len(results)} candidate papers. Checking open-access PDFs...")

        for item in results:
            if len(successful_papers) >= MAX_PAPERS:
                break

            pdf_url = item.openAccessPdf['url'] if item.openAccessPdf else None
            if not pdf_url:
                continue

            title = item.title
            st.write(f"Downloading PDF: {title} ({item.year})")

            pdf_path = download_pdf(pdf_url, f"{len(successful_papers)+1}_{title}")
            if pdf_path:
                sections = extract_sections(pdf_path)

                paper = {
                    "title": title,
                    "authors": [a['name'] for a in item.authors],
                    "year": item.year,
                    "abstract": item.abstract or "No abstract available",
                    "citations": item.citationCount or 0,
                    "pdf_file": os.path.basename(pdf_path),
                    "sections": sections
                }
                successful_papers.append(paper)
                st.success(f"Added paper {len(successful_papers)}/{MAX_PAPERS}")

    return successful_papers

def download_pdf(pdf_url: str, title_prefix: str) -> str | None:
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title_prefix)[:100]
    filename = f"{safe_title}.pdf"
    path = os.path.join(PAPERS_FOLDER, filename)

    try:
        response = requests.get(pdf_url, stream=True, timeout=120)
        if response.status_code == 200:
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return path
        else:
            st.warning(f"Download failed (HTTP {response.status_code})")
    except Exception as e:
        st.warning(f"Download error: {str(e)}")
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
    except Exception as e:
        st.warning(f"Extraction failed: {str(e)}")
        return {"error": str(e)}

# ========================
# Streamlit UI
# ========================
st.set_page_config(page_title="AI Paper Retrieval & Extraction", layout="wide")
st.title("🧠 AI System to Automatically Review and Summarize Research Papers")
st.markdown("**Research Phase + Analysis Phase (Semantic Scholar only)**")

topic = st.text_input("Enter research topic", value="attention is all you need")

if st.button("🔥 Start Retrieval & Extraction", type="primary"):
    papers = search_and_collect_papers(topic)

    if papers:
        # Save dataset
        with open(DATASET_FILE, "w", encoding="utf-8") as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)

        st.success(f"🎉 Collected {len(papers)} papers with full text!")
        st.download_button(
            label="💾 Download dataset.json",
            data=json.dumps(papers, indent=2, ensure_ascii=False),
            file_name="dataset.json",
            mime="application/json"
        )

        # Show collected papers summary
        st.write("### Collected Papers")
        for i, p in enumerate(papers, 1):
            with st.expander(f"{i}. {p['title']} ({p['year']})"):
                st.write("**Authors**: " + ", ".join(p['authors']))
                st.write("**Citations**: " + str(p['citations']))
                st.write("**Abstract**: " + p['abstract'][:300] + "...")
                st.write("**Extracted Sections**: " + ", ".join(list(p['sections'].keys())))
    else:
        st.error("No papers with open-access PDFs found. Try a more specific topic.")

st.caption("Built with Streamlit • Semantic Scholar API • PyMuPDF4LLM")
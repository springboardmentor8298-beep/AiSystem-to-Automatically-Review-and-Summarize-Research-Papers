import os
import json
import streamlit as st
import requests
from semanticscholar import SemanticScholar
import pymupdf4llm
from dotenv import load_dotenv
from io import BytesIO

# Load .env file (secure API keys)
load_dotenv()

# Semantic Scholar API key (from .env)
S2_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
sch = SemanticScholar(api_key=S2_API_KEY) if S2_API_KEY else SemanticScholar()

# Folders & files
PAPERS_FOLDER = "papers"
DATASET_FILE = "dataset.json"
os.makedirs(PAPERS_FOLDER, exist_ok=True)

MAX_PAPERS = 10  # As per your document (up to 3–10, adjustable)

# ========================
# Research Phase: Search & PDF Retrieval
# ========================
def search_and_collect_papers(topic: str):
    st.write(f" Research Phase: Searching Semantic Scholar for **{topic}**")
    st.write(f"Goal: Collect up to {MAX_PAPERS} papers with open-access PDFs")

    successful_papers = []
    batch_size = 50

    with st.spinner("Searching papers..."):
        try:
            results = list(sch.search_paper(
                query=topic,
                limit=batch_size,
                fields=['title', 'authors', 'year', 'abstract', 'openAccessPdf', 'citationCount']
            ))
        except Exception as e:
            st.error(f"Search failed: {str(e)}. Check API key or internet.")
            return []

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
            st.write(f"Downloading: {title} ({item.year})")

            pdf_content = download_pdf_in_memory(pdf_url)
            pdf_path = save_pdf_locally(pdf_content, title) if pdf_content else None

            if pdf_content:
                sections = extract_sections_from_memory(pdf_content)

                paper = {
                    "title": title,
                    "authors": [a['name'] for a in item.authors],
                    "year": item.year,
                    "abstract": item.abstract or "No abstract available",
                    "citations": item.citationCount or 0,
                    "pdf_url": pdf_url,
                    "sections": sections
                }
                successful_papers.append(paper)
                st.success(f"Added paper {len(successful_papers)}/{MAX_PAPERS}")

                # Show temporary PDF viewer
                st.markdown(f"**Temporary PDF View** (scroll to see):")
                st.markdown(f'<iframe src="{pdf_url}" width="100%" height="500px"></iframe>', unsafe_allow_html=True)

    return successful_papers

def download_pdf_in_memory(pdf_url: str) -> bytes | None:
    try:
        response = requests.get(pdf_url, timeout=120)
        if response.status_code == 200:
            return response.content
        st.warning(f"Download failed (HTTP {response.status_code})")
    except Exception as e:
        st.warning(f"Download error: {str(e)}")
    return None

def save_pdf_locally(pdf_content: bytes, title: str) -> str | None:
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)[:100]
    filename = f"{safe_title}.pdf"
    path = os.path.join(PAPERS_FOLDER, filename)
    try:
        with open(path, "wb") as f:
            f.write(pdf_content)
        return path
    except:
        return None

def extract_sections_from_memory(pdf_content: bytes) -> dict:
    try:
        # Load PDF from memory
        doc = pymupdf4llm.open_stream(BytesIO(pdf_content))
        md_text = pymupdf4llm.to_markdown(doc)

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
st.title(" AI System to Automatically Review and Summarize Research Papers")
st.markdown("**Research Phase + Analysis Phase (Semantic Scholar only)**")

topic = st.text_input("Enter research topic", value="")

if st.button(" Start Retrieval & Extraction", type="primary"):
    papers = search_and_collect_papers(topic)

    if papers:
        # Save dataset for future use
        with open(DATASET_FILE, "w", encoding="utf-8") as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)

        st.success(f" Collected {len(papers)} papers with full text extraction!")
        st.download_button(
            label=" Download dataset.json (with extracted sections)",
            data=json.dumps(papers, indent=2, ensure_ascii=False),
            file_name="dataset.json",
            mime="application/json"
        )

        # Summary of collected papers
        st.write("### Collected Papers (PDFs displayed above)")
        for i, p in enumerate(papers, 1):
            with st.expander(f"{i}. {p['title']} ({p['year']})"):
                st.write("**Authors**: " + ", ".join(p['authors']))
                st.write("**Citations**: " + str(p['citations']))
                st.write("**Abstract**: " + p['abstract'][:300] + "...")
                st.write("**Extracted Sections**: " + ", ".join(list(p['sections'].keys())))
    else:
        st.error("No papers with open-access PDFs found. Try a more specific topic.")

st.caption("Built with Streamlit • Semantic Scholar API • PyMuPDF4LLM")
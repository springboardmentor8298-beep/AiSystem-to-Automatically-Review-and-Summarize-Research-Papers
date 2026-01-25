

import streamlit as st
import requests
import json
import time
import os
from dotenv import load_dotenv
from google import genai
from google.genai.types import HttpOptions

# =========================
# ENV & GEMINI CONFIG
# =========================
load_dotenv()
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")

if not GEMINI_KEY:
    st.error("GOOGLE_API_KEY missing in .env file")
    st.stop()

client = genai.Client(
    api_key=GEMINI_KEY,
    http_options=HttpOptions(api_version="v1beta")
)

# =========================
# SEMANTIC SCHOLAR SEARCH
# =========================
def search_papers(topic, limit):
    url = (
        "https://api.semanticscholar.org/graph/v1/paper/search"
        f"?query={topic}&limit={limit}&fields=title,abstract,tldr"
    )

    try:
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            return res.json().get("data", [])
    except:
        pass
    return []

# =========================
# STREAMLIT UI
# =========================
st.set_page_config(page_title="Research paper summarizer", layout="wide")
st.title("Research paper summarizer")

col1, col2 = st.columns([3, 1])
with col1:
    topic = st.text_input("Research Topic", "Artificial Intelligence")
with col2:
    paper_count = st.selectbox("Paper Count", [3, 5, 10, 15], index=1)

# =========================
# MAIN ACTION
# =========================
if st.button("🚀 Execute Search", type="primary"):
    with st.spinner("Searching papers and generating research sections..."):
        papers = search_papers(topic, paper_count)

        if not papers:
            st.error("No papers found.")
            st.stop()

        dataset = []
        for p in papers:
            dataset.append({
                "title": p.get("title"),
                "summary": p.get("tldr", {}).get("text") or p.get("abstract") or ""
            })

        prompt = f"""
You are an academic research writer.

Using the following literature on "{topic}", generate:

Abstract
Introduction
Methods (survey / conceptual)
Conclusion
References (paper titles only)

Rules:
- Academic tone
- Each section title must appear exactly as written above
- Do NOT use numbering like 1., 2., 3.
- Do NOT use **, ##, or markdown formatting
- No mention of AI tools

Literature:
{json.dumps(dataset, ensure_ascii=False)}
"""

        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )
            output = response.text
        except Exception as e:
            st.error(e)
            st.stop()

    # =========================
    # DISPLAY IN COLUMNS
    # =========================
    st.markdown("---")
    st.subheader("📄 Generated Research Paper")

    # left, right = st.columns(2)

    # with left:
    st.markdown("### 🧠 Abstract")
    st.markdown(output.split("Introduction")[0])
    st.divider()

    st.markdown("### 📘 Introduction")
    st.markdown(
        "Introduction" + output.split("Introduction")[1].split("Methods")[0]
    )
    st.divider()

    st.markdown("### 🧪 Methods")
    st.markdown(
        "Methods" + output.split("Methods")[1].split("Conclusion")[0]
    )
    st.divider()

    # with right:
    st.markdown("### 🧾 Conclusion")
    st.markdown(
        "Conclusion" + output.split("Conclusion")[1].split("References")[0]
    )
    st.divider()

    st.markdown("### 📚 References")
    st.markdown(
        "References" + output.split("References")[1]
    )


import streamlit as st
import requests
import json
import time 
import os
from google import genai
from google.genai.types import HttpOptions
from dotenv import load_dotenv

# --- 1. Configurations ---
load_dotenv()
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")

# Client setup using v1beta for Gemini 3 Flash Preview
client = genai.Client(
    api_key=GEMINI_KEY,
    http_options=HttpOptions(api_version="v1beta")
)

# --- 2. Professional UI Styling (Removes AI/Streamlit Branding) ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            #stDecoration {display:none;}
            </style>
            """
#st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 3. The Stable Search Function ---
def stable_search(query, limit=5):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={limit}&fields=title,abstract,url,year,tldr"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    }

    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                return response.json().get('data', [])
            elif response.status_code == 429:
                wait_time = (attempt + 1) * 30
                st.warning(f"Rate limited. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                st.error(f"Network Error: {response.status_code}")
                return []
        except Exception as e:
            st.error(f"Connection failed: {e}")
            return []
    return []

# --- 4. UI Layout ---
st.title("🔬 Research Synthesis Suite")

tab1, tab2 = st.tabs(["🔍 Search & Preview", "✍️ Analysis & Gaps"])

with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.text_input("Research Topic", "Artificial Intelligence")
    with col2:
        num_papers = st.selectbox("Paper Count", [1, 3, 5, 10,13,15,17,20], index=2)

    if st.button("🚀 Execute Search", type="primary"):
        with st.spinner("Accessing Academic Databases..."):
            results = stable_search(topic, limit=num_papers)
            
            if results:
                papers_data = []
                for item in results:
                    summary = item.get('tldr', {}).get('text') if item.get('tldr') else item.get('abstract')
                    
                    papers_data.append({
                        "title": item.get('title'),
                        "summary": summary if summary else "No abstract available.",
                        "url": item.get('url')
                    })
                    
                    with st.expander(f"📄 {item.get('title')}"):
                        st.write(summary)
                        st.caption(f"[Source Link]({item.get('url')})")
                
                with open("dataset.json", "w") as f:
                    json.dump(papers_data, f)
                st.success(f"Successfully cached {len(papers_data)} papers. Proceed to Analysis tab.")

    # Reset Button
    if os.path.exists("dataset.json"):
        if st.button("🗑️ Clear Local Cache"):
            os.remove("dataset.json")
            st.rerun()

with tab2:
    if os.path.exists("dataset.json"):
        with open("dataset.json", "r") as f:
            data = json.load(f)
        
        st.subheader("Deep Analysis & Research Gap Detection")
        if st.button("✨ Synthesize & Identify Gaps"):
            if not data:
                st.warning("No data found to analyze.")
            else:
                with st.spinner("Synthesizing literature and detecting gaps..."):
                    # The Enhanced Prompt
                    prompt = f"""
                    You are a professional academic reviewer. Perform a deep analysis on the following papers:
                    1. **Literature Review**: Create a formal synthesis of the core findings.
                    2. **Research Gaps**: Identify 3 specific areas where current knowledge is missing or limited based on these texts.
                    3. **Future Directions**: Suggest a novel study title to address these gaps.
                    
                    Strictly format the output with professional headers. 
                    Do not mention yourself as an AI or mention Gemini.
                    
                    DATASET:
                    {json.dumps(data)}
                    """
                    
                    try:
                        response = client.models.generate_content(
                            model="gemini-3-flash-preview", 
                            contents=prompt
                        )
                        st.markdown("---")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Processing Error: {e}")
    else:
        st.info("No active dataset. Please complete a search in the first tab.")
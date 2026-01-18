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

# 2026 SETUP: Using v1beta for Gemini 3 Flash Preview access
client = genai.Client(
    api_key=GEMINI_KEY,
    http_options=HttpOptions(api_version="v1beta")
)

# --- 2. The Stable Search Function (Your exact code) ---
def stable_search(query, limit=5):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={limit}&fields=title,abstract,url,year,tldr"
    
    # Use a real browser User-Agent to avoid being flagged as a bot
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    }

    for attempt in range(3): # Try 3 times
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                return response.json().get('data', [])
            elif response.status_code == 429:
                wait_time = (attempt + 1) * 30 # Wait 30s, then 60s
                st.warning(f"Rate limited. Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                st.error(f"API Error: {response.status_code}")
                return []
        except Exception as e:
            st.error(f"Connection failed: {e}")
            return []
    return []

# --- 3. UI Layout ---
st.set_page_config(page_title="Research Assistant", layout="wide")
st.title(" Research Assistant ")

tab1, tab2 = st.tabs(["🔍 Search & Preview", "✍️ AI Review"])

with tab1:
    # Your exact search UI
    topic = st.text_input("Topic", "Artificial Intelligence")
    num_papers = st.slider("Papers", 1, 10, 5)

    if st.button(" Start Stable Search"):
        with st.spinner("Fetching..."):
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
                
                with open("dataset.json", "w") as f:
                    json.dump(papers_data, f)
                st.success("Fetched successfully! Now go to the 'AI Review' tab.")

with tab2:
    if os.path.exists("dataset.json"):
        with open("dataset.json", "r") as f:
            data = json.load(f)
        
        st.subheader("Generate AI Synthesis")
        if st.button("✨ Write Review with Gemini 3"):
            if not data:
                st.warning("No papers found. Search in Tab 1 first.")
            else:
                with st.spinner("Gemini is analyzing the summaries..."):
                    # We pass the JSON data directly to the prompt
                    prompt = f"Synthesize these research paper summaries into a formal literature review with citations:\n\n{json.dumps(data)}"
                    
                    try:
                        response = client.models.generate_content(
                            model="gemini-3-flash-preview", 
                            contents=prompt
                        )
                        st.markdown("### Literature Review")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"AI Error: {e}")
    else:
        st.info("Please fetch papers in the first tab to see the AI options.")
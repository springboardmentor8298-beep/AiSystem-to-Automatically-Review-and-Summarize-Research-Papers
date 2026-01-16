import os
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv()

TEXT_DIR = "app/papers/text"
OUTPUT_DIR = "app/output"

MODEL = "facebook/bart-large-cnn"
API_KEY = os.getenv("HUGGINGFACE_API_KEY")


def hf_summarize(text: str) -> str:
    """
    Summarizes text using HuggingFace Inference API
    """
    url = f"https://router.huggingface.co/hf-inference/models/{MODEL}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": text[:2000],
        "parameters": {"min_length": 120, "max_length": 300}
    }

    for attempt in range(3):
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=60)
            res.raise_for_status()
            return res.json()[0]["summary_text"]
        except Exception as e:
            print(f"⚠ HF error attempt {attempt + 1}: {e}")
            time.sleep(2)

    return "Summarization failed due to API issues."


def analyze_all():
    """
    Reads extracted paper text + metadata
    Generates summaries with title, authors, year
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    combined_results = []

    if not os.path.exists(TEXT_DIR):
        print("❌ No extracted text found.")
        return None

    text_files = [f for f in os.listdir(TEXT_DIR) if f.endswith(".txt")]

    for file in text_files:
        print(f"📘 Analyzing {file}")

        # ---------- Read extracted text ----------
        with open(os.path.join(TEXT_DIR, file), "r", encoding="utf-8") as f:
            text = f.read()

        summary = hf_summarize(text)

        # ---------- Read metadata (Change 3) ----------
        meta_path = os.path.join(
            TEXT_DIR,
            file.replace(".txt", "_meta.json")
        )

        title = file.replace(".txt", "")
        authors = []
        year = "N/A"

        if os.path.exists(meta_path):
            meta = json.load(open(meta_path, "r", encoding="utf-8"))
            title = meta.get("title", title)
            authors = meta.get("authors", [])
            year = meta.get("year", "N/A")

        # ---------- Final structured result ----------
        result = {
            "title": title,
            "authors": authors,
            "year": year,
            "summary": summary
        }

        combined_results.append(result)

        # Save individual summary
        out_file = file.replace(".txt", "_summary.json")
        with open(os.path.join(OUTPUT_DIR, out_file), "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

        print(f"✅ Saved summary → {out_file}")

    # ---------- Save combined output ----------
    combined_path = os.path.join(OUTPUT_DIR, "combined_abstracts.json")
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(combined_results, f, indent=4, ensure_ascii=False)

    print(f"\n📊 Combined dataset ready → {combined_path}")
    return combined_results
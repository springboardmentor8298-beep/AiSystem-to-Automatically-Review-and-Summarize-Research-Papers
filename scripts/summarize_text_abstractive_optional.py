"""
Optional Abstractive Summarization using Hugging Face Router API
Falls back safely if API fails
"""

import os
import requests

HF_API_KEY = os.getenv("HF_API_KEY")
HF_API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

def abstractive_summarize(text, max_length=180, min_length=80):
    """
    Uses Hugging Face Router API for abstractive summarization.
    Returns None on failure.
    """

    if not HF_API_KEY:
        print("[INFO] HF_API_KEY not set. Skipping abstractive summarization.")
        return None

    payload = {
        "inputs": text[:6000],  # SAFETY LIMIT
        "parameters": {
            "max_length": max_length,
            "min_length": min_length,
            "do_sample": False
        }
    }

    try:
        response = requests.post(
            HF_API_URL,
            headers=HEADERS,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            print("[WARN] HF API error:", response.text)
            return None

        data = response.json()

        if isinstance(data, list) and "summary_text" in data[0]:
            return data[0]["summary_text"]

        return None

    except Exception as e:
        print("[WARN] HF API exception:", e)
        return None

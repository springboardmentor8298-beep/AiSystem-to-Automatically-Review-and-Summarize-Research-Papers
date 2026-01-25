"""
Safe Abstractive Summarization using Hugging Face Router API
- Handles long text via chunking
- Avoids HF crashes
- Rate-limit safe
"""

import os
import time
import requests
import re

HF_API_KEY = os.getenv("HF_API_KEY")

HF_API_URL = (
    "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
)

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

# -----------------------------
# CONFIG (IMPORTANT)
# -----------------------------
MAX_CHARS = 3000        # safe for BART
REQUEST_DELAY = 1.2     # prevents 429


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _chunk_text(text: str, max_chars=MAX_CHARS):
    chunks = []
    while len(text) > max_chars:
        split_at = text.rfind(".", 0, max_chars)
        if split_at == -1:
            split_at = max_chars
        chunks.append(text[:split_at])
        text = text[split_at:]
    chunks.append(text)
    return chunks


def abstractive_summarize(text: str) -> str:
    """
    Robust abstractive summarization.
    Returns None if HF fails (pipeline will fallback).
    """

    if not HF_API_KEY:
        return None

    text = _clean_text(text)

    if len(text) < 200:
        return None

    chunks = _chunk_text(text)

    summaries = []

    for chunk in chunks[:3]:  # 🔥 LIMIT API CALLS
        payload = {
            "inputs": chunk,
            "parameters": {
                "max_length": 150,
                "min_length": 60,
                "do_sample": False
            }
        }

        try:
            resp = requests.post(
                HF_API_URL,
                headers=HEADERS,
                json=payload,
                timeout=30
            )

            if resp.status_code != 200:
                print("[WARN] HF API error:", resp.text)
                return None

            data = resp.json()

            if isinstance(data, list) and "summary_text" in data[0]:
                summaries.append(data[0]["summary_text"])

            time.sleep(REQUEST_DELAY)

        except Exception as e:
            print("[WARN] HF request failed:", e)
            return None

    final_summary = " ".join(summaries).strip()
    return final_summary if len(final_summary) > 80 else None

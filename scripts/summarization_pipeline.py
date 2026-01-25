"""
Academic-grade summarization pipeline
- Chunked abstractive summarization
- Redundancy control
- Extractive fallback
"""

import re

try:
    from scripts.summarize_text_abstractive_optional import abstractive_summarize
except Exception:
    abstractive_summarize = None

from scripts.summarize_text_extractive_simple import extractive_summary


def chunk_text(text: str, max_chars=900):
    chunks, current = [], ""
    for para in text.split("\n\n"):
        if len(current) + len(para) < max_chars:
            current += " " + para
        else:
            chunks.append(current.strip())
            current = para
    if current.strip():
        chunks.append(current.strip())
    return chunks


def deduplicate_sentences(text: str) -> str:
    seen = set()
    sentences = re.split(r'(?<=[.!?])\s+', text)
    final = []
    for s in sentences:
        key = s.lower().strip()
        if len(key) > 30 and key not in seen:
            seen.add(key)
            final.append(s.strip())
    return " ".join(final)


def generate_summary(text: str) -> str:
    if not text or len(text.strip()) < 200:
        return ""

    # 🔑 CHUNKED ABSTRACTIVE (PRIMARY)
    if abstractive_summarize:
        summaries = []
        for chunk in chunk_text(text):
            try:
                s = abstractive_summarize(chunk)
                if s:
                    summaries.append(s.strip())
            except Exception:
                continue

        if summaries:
            merged = " ".join(summaries)
            return deduplicate_sentences(merged)

    # 🔁 FALLBACK (CLEAN EXTRACTIVE)
    return extractive_summary(text)

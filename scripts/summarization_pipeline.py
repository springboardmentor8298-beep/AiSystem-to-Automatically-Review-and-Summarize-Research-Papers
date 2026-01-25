"""
Main summarization pipeline
Uses Hugging Face Router API (abstractive)
Falls back to extractive summarization safely
"""

# --------------------------------------------------
# OPTIONAL ABSTRACTIVE (HF API)
# --------------------------------------------------
try:
    from scripts.summarize_text_abstractive_optional import abstractive_summarize
except Exception as e:
    print("[WARN] Abstractive summarization unavailable:", e)
    abstractive_summarize = None

# --------------------------------------------------
# REQUIRED EXTRACTIVE
# --------------------------------------------------
from scripts.summarize_text_extractive_simple import extractive_summary


def generate_summary(text):
    """
    Try abstractive summarization first.
    Fallback to extractive if HF fails.
    """

    if abstractive_summarize:
        try:
            summary = abstractive_summarize(text)
            if summary and isinstance(summary, str):
                return summary
        except Exception as e:
            print("[WARN] HF summarization failed:", e)

    print("[INFO] Using extractive summarization")
    return extractive_summary(text)

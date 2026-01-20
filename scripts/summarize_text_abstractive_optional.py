"""
Optional Abstractive Summarization using Transformers
Falls back safely if transformers/torch are unavailable
"""

import os

TRANSFORMERS_AVAILABLE = False

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except Exception as e:
    print("[INFO] Transformers not available. Falling back to extractive summary.")

def abstractive_summarize(text, max_length=200, min_length=80):
    """
    Generates abstractive summary if transformers are available.
    Returns None if not available.
    """
    if not TRANSFORMERS_AVAILABLE:
        return None

    try:
        summarizer = pipeline(
            "summarization",
            model="t5-small",
            tokenizer="t5-small",
            framework="pt"
        )

        summary = summarizer(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False
        )

        return summary[0]["summary_text"]

    except Exception as e:
        print("[WARN] Abstractive summarization failed:", e)
        return None


if __name__ == "__main__":
    sample_text = """
    Attention is all you need introduces the Transformer architecture
    based solely on attention mechanisms, dispensing with recurrence
    and convolutions entirely.
    """

    result = abstractive_summarize(sample_text)

    if result:
        print("Abstractive Summary:\n", result)
    else:
        print("Abstractive summarization not available.")

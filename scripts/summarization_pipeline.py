"""
Main summarization pipeline
Chooses abstractive if available, otherwise extractive
"""

import os

# --------------------------------------------------
# SAFE OPTIONAL IMPORT
# --------------------------------------------------
try:
    from scripts.summarize_text_abstractive_optional import abstractive_summarize
except Exception as e:
    print("[WARN] Abstractive summarization not available:", e)
    abstractive_summarize = None

# --------------------------------------------------
# REQUIRED EXTRACTIVE IMPORT
# --------------------------------------------------
from scripts.summarize_text_extractive_simple import extractive_summary


def generate_summary(text):
    """
    Try abstractive summarization first.
    Fallback to extractive if unavailable.
    """

    if abstractive_summarize is not None:
        try:
            summary = abstractive_summarize(text)
            if summary and isinstance(summary, str):
                return summary
        except Exception as e:
            print("[WARN] Abstractive summarization failed:", e)

    print("[INFO] Using extractive summarization")
    return extractive_summary(text)


if __name__ == "__main__":

    TEXT_PATH = os.path.join(
        "data", "text", "sample_attention_is_all_you_need.txt"
    )

    print("Reading text...")
    with open(TEXT_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    print("Generating summary...")
    final_summary = generate_summary(text)

    print("\nFINAL SUMMARY:\n")
    print(final_summary)

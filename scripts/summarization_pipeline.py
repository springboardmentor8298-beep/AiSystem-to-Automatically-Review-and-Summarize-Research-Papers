"""
Main summarization pipeline
Chooses abstractive if available, otherwise extractive
"""

from summarize_text_abstractive_optional import abstractive_summarize
from summarize_text_extractive_simple import extractive_summary


def generate_summary(text):
    """
    Try abstractive summarization first.
    Fallback to extractive if unavailable.
    """
    summary = abstractive_summarize(text)

    if summary is None:
        print("[INFO] Using extractive summarization")
        summary = extractive_summary(text)

    return summary


if __name__ == "__main__":
    with open("data/text/sample_attention_is_all_you_need.txt", "r", encoding="utf-8") as f:
        text = f.read()

    final_summary = generate_summary(text)
    print("\nFINAL SUMMARY:\n")
    print(final_summary)

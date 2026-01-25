"""
Improved Extractive Summarization
- Cleans broken PDF text
- Filters noisy sentences
- Produces readable summaries
"""

import re
from collections import Counter

# --------------------------------------------------
# TEXT CLEANING (CRITICAL FOR PDF OUTPUT)
# --------------------------------------------------

def clean_pdf_text(text: str) -> str:
    """
    Normalize PDF extracted text:
    - Fix broken word joins
    - Remove excessive whitespace
    """
    if not text:
        return ""

    # Remove excessive newlines
    text = re.sub(r'\n+', ' ', text)

    # Fix broken camelcase words: "TotrainMusicLM" → "To train Music LM"
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)

    # Normalize spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def split_sentences(text: str):
    """Split text into sentences"""
    return re.split(r'(?<=[.!?])\s+', text)


def build_word_frequencies(sentences):
    """Build word frequency table"""
    freq = Counter()
    for sentence in sentences:
        words = re.findall(r'\b[a-zA-Z]{3,}\b', sentence.lower())
        freq.update(words)
    return freq


def score_sentences(sentences, word_freq):
    """Score sentences based on word importance"""
    scores = {}

    for sentence in sentences:
        words = re.findall(r'\b[a-zA-Z]{3,}\b', sentence.lower())

        # Ignore very short or very long junk sentences
        if len(words) < 8 or len(words) > 40:
            continue

        score = sum(word_freq.get(word, 0) for word in words)
        scores[sentence] = score

    return scores


# --------------------------------------------------
# PUBLIC API
# --------------------------------------------------

def extractive_summary(text: str, top_n: int = 6) -> str:
    """
    Generate readable extractive summary
    """

    text = clean_pdf_text(text)
    sentences = split_sentences(text)

    if not sentences:
        return ""

    word_freq = build_word_frequencies(sentences)
    sentence_scores = score_sentences(sentences, word_freq)

    if not sentence_scores:
        return ""

    ranked = sorted(
        sentence_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    summary_sentences = [s for s, _ in ranked[:top_n]]
    return " ".join(summary_sentences)


# --------------------------------------------------
# CLI TEST (OPTIONAL)
# --------------------------------------------------
if __name__ == "__main__":
    sample_text = """
    TotrainMusicLM,weextracttherepresentationReAco...
    MusicLM introduces a hierarchical framework for music generation.
    """

    print(extractive_summary(sample_text))

import re

COMMON_WORDS = [
    "the", "and", "to", "of", "in", "for", "is", "are", "with", "that",
    "this", "from", "by", "as", "an", "be", "or", "it", "we", "our",
    "used", "using", "make", "makes", "making", "system", "model",
    "data", "algorithm", "learning", "results", "method", "approach"
]

def split_long_words(text: str) -> str:
    """
    Repairs PDF word-collapsing like:
    suggestproductstobuy -> suggest products to buy
    """
    def repair(match):
        word = match.group(0)
        repaired = word
        for w in COMMON_WORDS:
            repaired = re.sub(rf'(?<!\s){w}(?!\s)', f' {w} ', repaired)
        return repaired

    # Only apply to very long lowercase words (safe heuristic)
    return re.sub(r'\b[a-z]{15,}\b', repair, text)


def clean_text_for_summary(text: str) -> str:
    if not text:
        return ""

    # Remove references
    text = re.sub(r'\nreferences.*$', '', text, flags=re.I | re.S)

    # Fix camelCase
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)

    # Fix punctuation spacing
    text = re.sub(r'([.,;:!?])(?=[A-Za-z])', r'\1 ', text)

    # Fix digit-word collisions
    text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)

    # 🔥 FIX lowercase word collapsing
    text = split_long_words(text)

    # Remove citations
    text = re.sub(r'\[[0-9,\s]+\]', '', text)
    text = re.sub(r'\([A-Za-z].*?\d{4}\)', '', text)

    # Normalize spacing
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()

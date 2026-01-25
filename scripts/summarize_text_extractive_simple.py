import re
from collections import Counter


def clean_pdf_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)
    return text.strip()


def split_sentences(text: str):
    return re.split(r'(?<=[.!?])\s+', text)


def extractive_summary(text: str, top_n=5) -> str:
    text = clean_pdf_text(text)
    sentences = split_sentences(text)

    valid = [
        s for s in sentences
        if 12 <= len(s.split()) <= 35 and s[0].isupper()
    ]

    if not valid:
        return ""

    freq = Counter(
        w.lower() for s in valid for w in re.findall(r'\b[a-zA-Z]{3,}\b', s)
    )

    scored = {
        s: sum(freq[w.lower()] for w in re.findall(r'\b[a-zA-Z]{3,}\b', s))
        for s in valid
    }

    best = sorted(scored, key=scored.get, reverse=True)[:top_n]
    return " ".join(best)

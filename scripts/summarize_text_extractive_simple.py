import os
import re
from collections import Counter

TEXT_DIR = "data/text"
SUMMARY_DIR = "outputs/summaries"

os.makedirs(SUMMARY_DIR, exist_ok=True)

def read_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return sentences

def build_word_frequencies(sentences):
    freq = Counter()
    for sentence in sentences:
        words = re.findall(r'\b[a-zA-Z]+\b', sentence.lower())
        freq.update(words)
    return freq

def score_sentences(sentences, word_freq):
    scores = {}
    for sentence in sentences:
        words = re.findall(r'\b[a-zA-Z]+\b', sentence.lower())
        score = sum(word_freq[word] for word in words)
        scores[sentence] = score
    return scores

def summarize(text, top_n=8):
    sentences = split_sentences(text)
    word_freq = build_word_frequencies(sentences)
    sentence_scores = score_sentences(sentences, word_freq)

    ranked = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
    summary_sentences = [s for s, _ in ranked[:top_n]]

    return " ".join(summary_sentences)

if __name__ == "__main__":
    input_file = "sample_attention_is_all_you_need.txt"
    input_path = os.path.join(TEXT_DIR, input_file)

    print("Reading text...")
    text = read_text(input_path)

    print("Generating extractive summary...")
    summary = summarize(text)

    output_file = "attention_is_all_you_need_summary.txt"
    output_path = os.path.join(SUMMARY_DIR, output_file)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)

    print("Summary saved at:", output_path)

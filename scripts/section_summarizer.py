import os
import json
import re
from collections import Counter

SECTIONS_DIR = "outputs/sections"
SUMMARY_DIR = "outputs/section_summaries"

os.makedirs(SUMMARY_DIR, exist_ok=True)

def split_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text)

def word_frequencies(sentences):
    freq = Counter()
    for sentence in sentences:
        words = re.findall(r'\b[a-zA-Z]+\b', sentence.lower())
        freq.update(words)
    return freq

def summarize_section(text, max_sentences=3):
    sentences = split_sentences(text)
    if len(sentences) <= max_sentences:
        return text

    freq = word_frequencies(sentences)
    scores = {}

    for sentence in sentences:
        words = re.findall(r'\b[a-zA-Z]+\b', sentence.lower())
        scores[sentence] = sum(freq[word] for word in words)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    summary = [sentence for sentence, _ in ranked[:max_sentences]]

    return " ".join(summary)

if __name__ == "__main__":
    for file in os.listdir(SECTIONS_DIR):
        if file.endswith(".json"):
            print(f"Summarizing sections in {file}")

            with open(os.path.join(SECTIONS_DIR, file), "r", encoding="utf-8") as f:
                sections = json.load(f)

            summarized = {}
            for section, content in sections.items():
                summarized[section] = summarize_section(content)

            output_file = file.replace("_sections.json", "_section_summary.json")
            output_path = os.path.join(SUMMARY_DIR, output_file)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(summarized, f, indent=2)

            print(f"Saved section summaries to: {output_path}")

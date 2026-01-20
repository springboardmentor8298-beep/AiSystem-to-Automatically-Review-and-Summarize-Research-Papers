import json 
import re 
import sys

topic = sys.argv[1].strip().replace(" ", "_").lower() 

INPUT_FILE = f"extracted_text/{topic}_raw_text.json" 
OUTPUT_FILE = f"extracted_text/{topic}_section_text.json" 
def extract_section(text, start, end=None): 
    pattern = start + "(.*?)" + (end if end else "$") 
    match = re.search(pattern, text, re.IGNORECASE | 
                      re.DOTALL)
    return match.group(1).strip() if match else "" 
with open(INPUT_FILE, "r", encoding="utf-8") as f: 
    papers = json.load(f) 
results = [] 
for paper in papers: 
    text = paper["text"] 
    sections = { 
        "abstract": extract_section(text, "abstract", "introduction"), 
        "introduction": extract_section(text, "introduction", "method"), 
        "methodology": extract_section(text, "method", "result"), 
        "conclusion": extract_section(text, "conclusion") } 
    results.append({ 
        "pdf_file": paper["pdf_file"], 
        "sections": sections }) 
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f: 
        json.dump(results, f, indent=4) 
print("✅ Section-wise extraction completed.")
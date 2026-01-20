import json
import re 
from collections import Counter 
import sys

topic = sys.argv[1].strip().replace(" ", "_").lower() 

INPUT_FILE = f"extracted_text/{topic}_section_text.json" 
OUTPUT_FILE = f"analysis/{topic}_keywords.json" 

STOPWORDS = {
"the","and","is","to","of","in","for","with","we","our","that"} 

with open(INPUT_FILE, "r", encoding="utf-8") as f: 
    papers = json.load(f) 

    output = [] 
    for paper in papers: 
        text = " ".join(paper["sections"].values()).lower() 
        words = re.findall(r"\b[a-z]{4,}\b", text) 
        words = [w for w in words if w not in STOPWORDS]

        keywords = [w for w, _ in 
                    Counter(words).most_common(10)] 
        output.append({ 
            "pdf_file": paper["pdf_file"], 
            "keywords": keywords }) 

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f: 
            json.dump(output, f, indent=4) 
            
print("✅ Keywords extracted")
import json 
import sys

topic = sys.argv[1].strip().replace(" ", "_").lower() 

INPUT_FILE = f"extracted_text/{topic}_section_text.json" 
OUTPUT_FILE = f"analysis/{topic}_validation.txt" 
with open(INPUT_FILE, "r", encoding="utf-8") as f:
     papers = json.load(f)
     lines = [] 
     for paper in papers: 
         missing = [k for k,v in paper["sections"].items() if not v] 
         if missing: 
          lines.append(f"{paper['pdf_file']} ❌ Missing: {','.join(missing)}") 
         else: 
            lines.append(f"{paper['pdf_file']} ✅ All sections extracted") 
         with open(OUTPUT_FILE, "w", encoding="utf-8") as f: 
            f.write("\n".join(lines)) 
            print("✅ Validation completed")
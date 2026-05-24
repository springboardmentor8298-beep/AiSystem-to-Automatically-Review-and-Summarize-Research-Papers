import fitz  # PyMuPDF
from typing import Dict, List
import re
import os

class TextExtractionModule:
    def __init__(self):
        self.section_patterns = {
            'abstract': r'(?i)(abstract|summary)',
            'introduction': r'(?i)(introduction|background)',
            'methods': r'(?i)(methods|methodology|approach)',
            'results': r'(?i)(results|findings)',
            'discussion': r'(?i)(discussion|conclusion)',
            'references': r'(?i)(references|bibliography)'
        }
    
    def extract_pdf_text(self, pdf_path: str) -> Dict[str, str]:
        """Extract and structure text from PDF"""
        if not pdf_path or not os.path.exists(pdf_path):
            print(f"❌ PDF file not found: {pdf_path}")
            return {}
        
        print(f"📄 Opening PDF: {pdf_path}")
        
        try:
            # Check file size
            file_size = os.path.getsize(pdf_path)
            print(f"📄 File size: {file_size} bytes ({file_size / 1024:.1f} KB)")
            
            if file_size < 1000:
                print(f"⚠️ PDF file too small, may be corrupted")
                return {}
            
            # Open PDF - FIXED: removed fitz.fitz
            doc = fitz.open(pdf_path)
            print(f"📄 PDF has {len(doc)} pages")
            
            full_text = ""
            pages_with_text = 0
            
            for page_num, page in enumerate(doc):
                text = page.get_text()
                if text and text.strip():
                    full_text += text + "\n"
                    pages_with_text += 1
                    print(f"   Page {page_num + 1}: {len(text)} chars")
                else:
                    print(f"   Page {page_num + 1}: No text found")
            
            doc.close()
            
            print(f"📊 Total: {pages_with_text}/{len(doc)} pages with text")
            print(f"📊 Total characters: {len(full_text)}")
            
            if not full_text or len(full_text.strip()) < 100:
                print("⚠️ Very little text extracted")
                return {}
            
            # Return full text in a structured way
            sections = self._segment_sections(full_text)
            
            # Ensure we have at least full_text
            if not sections:
                sections = {'full_text': full_text}
            
            return sections
            
        except Exception as e:
            print(f"❌ PDF extraction error: {e}")
            return {}
    
    def _segment_sections(self, text: str) -> Dict[str, str]:
        """Segment text into sections"""
        sections = {}
        lines = text.split('\n')
        
        current_section = 'full_text'
        current_content = []
        
        for line in lines:
            if not line.strip():
                current_content.append(line)
                continue
                
            section_found = False
            for section, pattern in self.section_patterns.items():
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    if current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = section
                    current_content = []
                    section_found = True
                    print(f"   Found section: {section}")
                    break
            
            if not section_found:
                current_content.append(line)
        
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def extract_key_findings(self, text: str) -> List[str]:
        """Extract key findings from text"""
        if not text:
            return []
        
        print(f"📊 Extracting key findings from {len(text)} chars")
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Keywords that indicate findings
        indicators = [
            'found', 'shows', 'demonstrates', 'indicates', 'reveals',
            'significant', 'important', 'finding', 'result', 'suggests',
            'concludes', 'we observe', 'our analysis', 'we find',
            'contributes', 'demonstrate', 'propose', 'present',
            'achieve', 'outperform', 'state-of-the-art', 'novel'
        ]
        
        findings = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 30:
                continue
                
            for indicator in indicators:
                if indicator.lower() in sentence.lower():
                    findings.append(sentence)
                    break
        
        # Remove duplicates
        unique_findings = []
        for f in findings:
            if f not in unique_findings:
                unique_findings.append(f)
        
        print(f"📊 Found {len(unique_findings)} key findings")
        return unique_findings[:10]
    
    def extract_full_text(self, pdf_path: str) -> str:
        """Extract full text from PDF"""
        if not pdf_path or not os.path.exists(pdf_path):
            return ""
        
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            for page_num, page in enumerate(doc):
                text = page.get_text()
                if text:
                    full_text += text + "\n"
            doc.close()
            return full_text
        except Exception as e:
            print(f"❌ Full text extraction error: {e}")
            return ""
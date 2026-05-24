from typing import List, Dict, Set
from app.models.paper import Paper
from collections import Counter

class AnalysisModule:
    def __init__(self):
        self.stop_words = {'a', 'an', 'and', 'the', 'of', 'to', 'in', 'for', 'on', 'with', 'by', 'is', 'are', 'this', 'that', 'these', 'those'}
    
    def identify_key_themes(self, papers: List[Paper]) -> List[str]:
        """Identify common themes across papers"""
        all_text = " ".join([p.abstract + " " + " ".join(p.extracted_sections.get('discussion', '')) 
                            for p in papers if p])
        
        # Simple keyword extraction (can be enhanced with NLP)
        words = all_text.lower().split()
        word_freq = Counter([w for w in words if w not in self.stop_words and len(w) > 3])
        
        # Get top 20 keywords as potential themes
        themes = [word for word, _ in word_freq.most_common(20)]
        return themes[:10]  # Return top 10 themes
    
    def compare_methodologies(self, papers: List[Paper]) -> Dict:
        """Compare methodologies across papers"""
        comparison = {
            "common_approaches": [],
            "unique_methods": {},
            "data_sources": [],
            "analysis_techniques": []
        }
        
        for paper in papers:
            methods_text = paper.extracted_sections.get('methods', '')
            
            # Extract method types (simplified approach)
            if 'qualitative' in methods_text.lower():
                comparison['common_approaches'].append('Qualitative')
            if 'quantitative' in methods_text.lower():
                comparison['common_approaches'].append('Quantitative')
            if 'mixed' in methods_text.lower():
                comparison['common_approaches'].append('Mixed Methods')
            
            comparison['unique_methods'][paper.title] = methods_text[:200] + "..." if methods_text else "No methods section found"
        
        # Remove duplicates from common_approaches
        comparison['common_approaches'] = list(set(comparison['common_approaches']))
        
        return comparison
    
    def identify_overlaps(self, papers: List[Paper]) -> List[Dict]:
        """Identify overlapping findings or contradictions"""
        overlaps = []
        key_findings_all = []
        
        for paper in papers:
            key_findings_all.extend(paper.key_findings)
        
        # Find common themes in findings (simplified)
        finding_text = " ".join(key_findings_all).lower()
        
        # Identify contradictions (simplified - would need NLP for better results)
        contradictions = []
        for i, paper1 in enumerate(papers):
            for paper2 in papers[i+1:]:
                # Simple contradiction detection based on opposite keywords
                pos_keywords = ['increase', 'improve', 'positive', 'significant', 'beneficial']
                neg_keywords = ['decrease', 'reduce', 'negative', 'no significant', 'detrimental']
                
                findings1 = " ".join(paper1.key_findings).lower()
                findings2 = " ".join(paper2.key_findings).lower()
                
                for pk in pos_keywords:
                    if pk in findings1 and any(nk in findings2 for nk in neg_keywords):
                        contradictions.append({
                            "paper1": paper1.title,
                            "paper2": paper2.title,
                            "potential_contradiction": f"Paper 1 reports {pk} while Paper 2 reports contradictory finding"
                        })
                        break
        
        return contradictions
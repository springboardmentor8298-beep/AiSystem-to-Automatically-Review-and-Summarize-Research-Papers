from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import Config
from app.models.paper import Paper
from typing import List

class DraftGenerationModule:
    def __init__(self):
        # Check if we're using local GPT4All or OpenAI
        if Config.OPENAI_API_BASE:  # Using local GPT4All
            print(f"✅ Using local LLM at: {Config.OPENAI_API_BASE}")
            self.llm = ChatOpenAI(
                base_url=Config.OPENAI_API_BASE,
                model=Config.GPT_MODEL,
                temperature=Config.TEMPERATURE,
                api_key=Config.OPENAI_API_KEY,
                max_tokens=1024,  # ← ADDED: Ensures longer responses
                max_retries=2
            )
        elif Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != "not-needed":
            print("✅ Using OpenAI API")
            self.llm = ChatOpenAI(
                model=Config.GPT_MODEL,
                temperature=Config.TEMPERATURE,
                api_key=Config.OPENAI_API_KEY,
                max_tokens=1024,  # ← ADDED: Ensures longer responses
                max_retries=2
            )
        else:
            print("⚠️ No LLM configured. Using mock responses.")
            self.llm = None
    
    async def generate_abstract(self, papers: List[Paper], word_limit: int = 100) -> str:
        """Generate abstract with word limit and proper formatting"""
        if not self.llm or not papers:
            return self._generate_mock_abstract(papers, word_limit)
        
        # Limit input to prevent token overflow
        summary = self._format_papers_summary(papers)
        if len(summary) > 8000:
            summary = summary[:8000]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert academic writer. Write a concise, well-structured abstract for a systematic review.
            Use 2-3 short paragraphs. Keep it under 150 words. Do not use markdown headers."""),
            ("human", f"""
            Based on these {len(papers)} research papers, write a {word_limit}-word abstract.
            
            {summary}
            
            Write a complete abstract with: background, methods, key findings, and conclusion.
            Use double line breaks between paragraphs.
            """)
        ])
        
        try:
            # Bind max_tokens to ensure complete response
            chain = prompt | self.llm.bind(max_tokens=500) | StrOutputParser()
            result = await chain.ainvoke({})
            result = result.strip()
            
            if len(result) < 100:
                print(f"⚠️ Abstract too short ({len(result)} chars), using mock")
                return self._generate_mock_abstract(papers, word_limit)
            
            print(f"✅ Abstract generated: {len(result)} characters")
            return result
        except Exception as e:
            print(f"Abstract generation error: {e}")
            return self._generate_mock_abstract(papers, word_limit)
    
    async def generate_methods_comparison(self, papers: List[Paper]) -> str:
        """Generate methods comparison section with proper formatting"""
        if not self.llm or not papers:
            return self._generate_mock_methods_comparison(papers)
        
        # Limit input
        methods_details = self._format_methods_details(papers)
        if len(methods_details) > 6000:
            methods_details = methods_details[:6000]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert research methodologist.
            Use bullet points (starting with -) for key comparisons.
            Keep your response concise but informative (200-400 words)."""),
            ("human", f"""
            Compare the methodologies in these {len(papers)} papers:
            
            {methods_details}
            
            Write a methods comparison covering: approaches, similarities, differences, limitations.
            """)
        ])
        
        try:
            chain = prompt | self.llm.bind(max_tokens=600) | StrOutputParser()
            result = await chain.ainvoke({})
            result = result.strip()
            
            if len(result) < 100:
                return self._generate_mock_methods_comparison(papers)
            
            print(f"✅ Methods comparison generated: {len(result)} characters")
            return result
        except Exception as e:
            print(f"Methods generation error: {e}")
            return self._generate_mock_methods_comparison(papers)
    
    async def generate_results_synthesis(self, papers: List[Paper]) -> str:
        """Generate results synthesis with proper formatting"""
        if not self.llm or not papers:
            return self._generate_mock_results_synthesis(papers)
        
        # Limit input
        findings_details = self._format_findings_details(papers)
        if len(findings_details) > 6000:
            findings_details = findings_details[:6000]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at synthesizing research findings.
            Use bullet points for key findings. Keep response concise (200-400 words)."""),
            ("human", f"""
            Synthesize findings from these {len(papers)} papers:
            
            {findings_details}
            
            Identify: common themes, converging evidence, contradictions, gaps.
            """)
        ])
        
        try:
            chain = prompt | self.llm.bind(max_tokens=600) | StrOutputParser()
            result = await chain.ainvoke({})
            result = result.strip()
            
            if len(result) < 100:
                return self._generate_mock_results_synthesis(papers)
            
            print(f"✅ Results synthesis generated: {len(result)} characters")
            return result
        except Exception as e:
            print(f"Results generation error: {e}")
            return self._generate_mock_results_synthesis(papers)
    
    def generate_apa_references(self, papers: List[Paper]) -> List[str]:
        """Generate APA 7th edition references"""
        references = []
        for paper in papers:
            authors = []
            for i, author in enumerate(paper.authors[:6]):
                if ',' in author:
                    last, first = author.split(',', 1)
                    authors.append(f"{last.strip()}, {first.strip()[0]}.")
                else:
                    parts = author.split()
                    if len(parts) > 1:
                        authors.append(f"{parts[-1]}, {parts[0][0]}.")
                    else:
                        authors.append(author)
            
            author_str = ", ".join(authors) if authors else "Anonymous"
            if len(paper.authors) > 20:
                author_str += "…"
            
            reference = f"{author_str} ({paper.year}). {paper.title}. {paper.venue if paper.venue else 'Journal'}."
            references.append(reference)
        
        return references if references else ["No references available"]
    
    def _format_papers_summary(self, papers: List[Paper]) -> str:
        """Format papers with LIMITED content for LLM"""
        summary = []
        for idx, paper in enumerate(papers, 1):
            # Get the full extracted text
            full_text = paper.extracted_sections.get('full_text', '')
            if not full_text or len(full_text) < 100:
                full_text = paper.abstract or "No content available"
            
            # Limit to 2000 chars per paper (reduced from 5000)
            content_preview = full_text[:2000] if len(full_text) > 2000 else full_text
            
            summary.append(f"""
--- PAPER {idx}: {paper.title} ---
CONTENT:
{content_preview}

KEY FINDINGS: {', '.join(paper.key_findings[:3]) if paper.key_findings else 'None'}
""")
        return "\n".join(summary)
    
    def _format_methods_details(self, papers: List[Paper]) -> str:
        """Format papers with methods content (LIMITED)"""
        details = []
        for idx, paper in enumerate(papers, 1):
            methods = paper.extracted_sections.get('methods', '')
            if not methods or len(methods) < 100:
                methods = paper.extracted_sections.get('full_text', '')[:1500]
            
            details.append(f"""
PAPER {idx}: {paper.title}
METHODS: {methods[:1500]}
""")
        return "\n".join(details)
    
    def _format_findings_details(self, papers: List[Paper]) -> str:
        """Format papers with findings content (LIMITED)"""
        details = []
        for idx, paper in enumerate(papers, 1):
            results = paper.extracted_sections.get('results', '')
            if not results or len(results) < 100:
                results = paper.extracted_sections.get('full_text', '')[:1500]
            
            details.append(f"""
PAPER {idx}: {paper.title}
FINDINGS: {results[:1500]}
KEY FINDINGS SUMMARY: {', '.join(paper.key_findings[:3]) if paper.key_findings else 'None'}
""")
        return "\n".join(details)
    
    def _generate_mock_abstract(self, papers: List[Paper], word_limit: int) -> str:
        return f"""This systematic review analyzed {len(papers)} research papers on the selected topic.

The review synthesized findings from multiple studies to identify key themes and methodologies. Results indicate significant contributions to the field, though more research is needed in certain areas.

This review provides a comprehensive overview of current literature and identifies gaps for future investigation."""
    
    def _generate_mock_methods_comparison(self, papers: List[Paper]) -> str:
        return f"""**Methodology Overview**

The methodology comparison across {len(papers)} studies reveals diverse approaches:

- **Common Approaches**: Each study employed rigorous data collection and analysis procedures
- **Key Differences**: Variations in sample sizes and analytical techniques
- **Limitations**: Some studies lack standardized protocols

**Recommendations**: Future research should adopt more consistent methodologies."""
    
    def _generate_mock_results_synthesis(self, papers: List[Paper]) -> str:
        return f"""**Key Findings**

The synthesis of findings from {len(papers)} papers reveals several key themes:

- **Converging Evidence**: Multiple studies support the importance of this research area
- **Contradictions**: Some disagreements exist across studies, suggesting need for further investigation
- **Research Gaps**: Future work should address methodological inconsistencies

**Conclusion**: The body of evidence demonstrates meaningful contributions to the field."""
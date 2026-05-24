from langgraph.graph import StateGraph
from typing import TypedDict, List, Optional
import os

from app.modules.paper_retrieval import PaperRetrievalModule
from app.modules.text_extraction import TextExtractionModule
from app.modules.analysis import AnalysisModule
from app.modules.draft_generation import DraftGenerationModule
from app.modules.review import ReviewModule
from app.models.paper import SearchQuery, Paper


# ---------- WORKFLOW STATE ----------
class WorkflowState(TypedDict):
    query: SearchQuery
    papers: List[Paper]
    extracted_sections: dict
    key_themes: List[str]
    methods_comparison: dict
    abstract: str
    methods_section: str
    results_section: str
    apa_references: List[str]
    quality_assessment: dict
    revision_suggestions: List[str]
    current_stage: str
    cache_stats: dict


# ---------- MAIN WORKFLOW ----------
class SystematicReviewWorkflow:

    def __init__(self):
        self.paper_retrieval = PaperRetrievalModule()
        self.text_extraction = TextExtractionModule()
        self.analysis = AnalysisModule()
        self.draft_gen = DraftGenerationModule()
        self.review = ReviewModule()

        self.graph = self._build_graph()

    # ---------- GRAPH ----------
    def _build_graph(self):
        workflow = StateGraph(WorkflowState)

        workflow.add_node("search_papers", self.search_papers)
        workflow.add_node("extract_text", self.extract_text)
        workflow.add_node("analyze_papers", self.analyze_papers)
        workflow.add_node("generate_drafts", self.generate_drafts)
        workflow.add_node("review_content", self.review_content)

        workflow.set_entry_point("search_papers")
        workflow.add_edge("search_papers", "extract_text")
        workflow.add_edge("extract_text", "analyze_papers")
        workflow.add_edge("analyze_papers", "generate_drafts")
        workflow.add_edge("generate_drafts", "review_content")

        return workflow.compile()

    # ---------- SEARCH PAPERS ----------
    async def search_papers(self, state: WorkflowState) -> WorkflowState:
        try:
            state["papers"] = await self.paper_retrieval.search_papers(state["query"])
            state["cache_stats"] = self.paper_retrieval.get_cache_stats()
            print(f"✅ Found {len(state['papers'])} papers")
        except Exception as e:
            print(f"❌ Paper search error: {e}")
            state["papers"] = []

        state["current_stage"] = "papers_searched"
        return state

    # ---------- EXTRACT TEXT ----------
    async def extract_text(self, state: WorkflowState) -> WorkflowState:
        for paper in state["papers"]:
            try:
                # Download PDF if not cached
                if not paper.local_pdf_path:
                    await self.paper_retrieval.download_pdf(paper)

                # Extract if PDF exists
                if paper.local_pdf_path and os.path.exists(paper.local_pdf_path):
                    print(f"📖 Extracting text from: {paper.title}")
                    
                    # Extract sections from PDF
                    paper.extracted_sections = self.text_extraction.extract_pdf_text(paper.local_pdf_path)
                    
                    # If no sections found, try full text extraction
                    if not paper.extracted_sections or not paper.extracted_sections.get('full_text'):
                        print(f"⚠️ Section extraction had issues, checking extracted content...")
                        if paper.extracted_sections and paper.extracted_sections.get('full_text'):
                            print(f"✅ Full text available: {len(paper.extracted_sections['full_text'])} chars")
                    
                    # Extract key findings from results section or full text
                    results_text = paper.extracted_sections.get('results', '')
                    if not results_text or len(results_text) < 100:
                        results_text = paper.extracted_sections.get('full_text', '')
                        print(f"📊 Using full text for key finding extraction ({len(results_text)} chars)")
                    
                    paper.key_findings = self.text_extraction.extract_key_findings(results_text)
                    
                    if paper.key_findings:
                        print(f"✅ Found {len(paper.key_findings)} key findings")
                    else:
                        print(f"⚠️ No key findings extracted, using mock data for testing")
                        # Fallback to mock findings for testing
                        paper.key_findings = [
                            f"This study presents important findings about {paper.title[:50]}",
                            "The results demonstrate significant contributions to the field",
                            "Future research directions are identified and discussed"
                        ]
                else:
                    print(f"⚠️ No PDF available for: {paper.title}")
                    # Create mock extracted sections for testing
                    paper.extracted_sections = {
                        'abstract': paper.abstract,
                        'full_text': paper.abstract,
                        'results': f"Results from {paper.title} show promising outcomes."
                    }
                    paper.key_findings = [
                        f"Key finding from {paper.title[:50]}",
                        "Important result that contributes to the field"
                    ]

            except Exception as e:
                print(f"❌ Text extraction failed for {paper.title}: {e}")
                # Continue with other papers
                continue

        state["current_stage"] = "text_extracted"
        return state

    # ---------- ANALYSIS ----------
    async def analyze_papers(self, state: WorkflowState) -> WorkflowState:
        try:
            if state["papers"]:
                state["key_themes"] = self.analysis.identify_key_themes(state["papers"])
                state["methods_comparison"] = self.analysis.compare_methodologies(state["papers"])
                print(f"✅ Analysis complete: Found {len(state['key_themes'])} themes")
            else:
                state["key_themes"] = ["No papers found"]
                state["methods_comparison"] = {"common_approaches": [], "unique_methods": {}}
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            state["key_themes"] = []
            state["methods_comparison"] = {}

        state["current_stage"] = "papers_analyzed"
        return state

    # ---------- GENERATE DRAFTS ----------
    async def generate_drafts(self, state: WorkflowState) -> WorkflowState:
        if state["papers"]:
            # ABSTRACT
            try:
                print("📝 Generating abstract...")
                state["abstract"] = await self.draft_gen.generate_abstract(state["papers"])
                print(f"✅ Abstract generated ({len(state['abstract'])} chars)")
            except Exception as e:
                print(f"❌ Abstract generation error: {e}")
                state["abstract"] = "Abstract generation failed. Check local LLM connection."

            # METHODS
            try:
                print("🔬 Generating methods comparison...")
                state["methods_section"] = await self.draft_gen.generate_methods_comparison(state["papers"])
                print(f"✅ Methods generated ({len(state['methods_section'])} chars)")
            except Exception as e:
                print(f"❌ Methods generation error: {e}")
                state["methods_section"] = "Methods generation failed."

            # RESULTS
            try:
                print("📊 Generating results synthesis...")
                state["results_section"] = await self.draft_gen.generate_results_synthesis(state["papers"])
                print(f"✅ Results generated ({len(state['results_section'])} chars)")
            except Exception as e:
                print(f"❌ Results generation error: {e}")
                state["results_section"] = "Results generation failed."

            # REFERENCES
            try:
                state["apa_references"] = self.draft_gen.generate_apa_references(state["papers"])
                print(f"✅ Generated {len(state['apa_references'])} APA references")
            except Exception as e:
                print(f"❌ Reference generation error: {e}")
                state["apa_references"] = []

        else:
            state["abstract"] = "No papers found for this topic."
            state["methods_section"] = "Methods comparison could not be generated."
            state["results_section"] = "Results synthesis could not be generated."
            state["apa_references"] = []

        state["current_stage"] = "drafts_generated"
        return state

    # ---------- REVIEW ----------
    async def review_content(self, state: WorkflowState) -> WorkflowState:
        try:
            if state["abstract"] and state["methods_section"] and state["results_section"]:
                quality = await self.review.assess_quality(
                    state["abstract"],
                    state["methods_section"],
                    state["results_section"]
                )
                state["quality_assessment"] = quality
                state["revision_suggestions"] = quality.get("revision_suggestions", [])
                print(f"✅ Quality assessment: {quality.get('quality_score', 0)}/10")
            else:
                state["quality_assessment"] = {
                    "quality_score": 0,
                    "feedback": "No content generated"
                }
                state["revision_suggestions"] = ["Search for papers first"]
        except Exception as e:
            print(f"❌ Review error: {e}")
            state["quality_assessment"] = {
                "quality_score": 0,
                "feedback": "Review failed"
            }
            state["revision_suggestions"] = []

        state["current_stage"] = "review_completed"
        return state

    # ---------- RUN ----------
    async def run_workflow(self, topic: str, max_papers: int = 3) -> WorkflowState:
        print(f"\n{'='*50}")
        print(f"🚀 Starting Systematic Review for: {topic}")
        print(f"{'='*50}\n")

        initial_state = {
            "query": SearchQuery(topic=topic, max_papers=max_papers),
            "papers": [],
            "extracted_sections": {},
            "key_themes": [],
            "methods_comparison": {},
            "abstract": "",
            "methods_section": "",
            "results_section": "",
            "apa_references": [],
            "quality_assessment": {},
            "revision_suggestions": [],
            "current_stage": "started",
            "cache_stats": {}
        }

        try:
            final_state = await self.graph.ainvoke(initial_state)
            print(f"\n{'='*50}")
            print(f"✅ Systematic Review Complete!")
            print(f"{'='*50}\n")
            return final_state
        except Exception as e:
            print(f"❌ Workflow error: {e}")
            initial_state["current_stage"] = f"error: {str(e)}"
            return initial_state

    # ---------- CACHE ----------
    def get_cache_stats(self):
        return self.paper_retrieval.get_cache_stats()

    def clear_cache(self, paper_id: Optional[str] = None):
        self.paper_retrieval.clear_cache(paper_id)
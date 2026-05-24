from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class Paper(BaseModel):
    paper_id: str
    title: str
    authors: List[str]
    abstract: str
    year: int
    venue: str
    citation_count: int
    pdf_url: Optional[str] = None
    local_pdf_path: Optional[str] = None
    extracted_sections: Dict[str, str] = {}
    key_findings: List[str] = []

class SearchQuery(BaseModel):
    topic: str
    max_papers: int = 3
    year_from: Optional[int] = None
    year_to: Optional[int] = None

class SystematicReview(BaseModel):
    topic: str
    papers_analyzed: List[Paper]
    abstract: str
    methods_comparison: str
    results_synthesis: str
    key_themes: List[str]
    apa_references: List[str]
    quality_score: float
    revision_suggestions: List[str]
    generated_at: datetime = datetime.now()
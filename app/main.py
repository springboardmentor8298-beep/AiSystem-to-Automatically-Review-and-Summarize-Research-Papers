from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import threading
import uvicorn
from app.services.workflow_service import SystematicReviewWorkflow

app = FastAPI(title="AI Systematic Review System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReviewRequest(BaseModel):
    topic: str
    max_papers: Optional[int] = 3
    year_from: Optional[int] = None
    year_to: Optional[int] = None

@app.get("/")
async def root():
    return {
        "message": "AI Systematic Review System API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "POST /generate_review": "Generate systematic review",
            "GET /health": "Health check",
            "GET /docs": "API documentation"
        }
    }

@app.post("/generate_review")
async def generate_review(request: ReviewRequest):
    """Generate systematic review for a given topic"""
    try:
        workflow = SystematicReviewWorkflow()
        result = await workflow.run_workflow(request.topic, request.max_papers)
        
        return {
            "success": True,
            "topic": request.topic,
            "abstract": result.get('abstract', ''),
            "methods_comparison": result.get('methods_section', ''),
            "results_synthesis": result.get('results_section', ''),
            "references": result.get('apa_references', []),
            "key_themes": result.get('key_themes', []),
            "quality_score": result.get('quality_assessment', {}).get('quality_score', 0),
            "papers_analyzed": len(result.get('papers', [])),
            "revision_suggestions": result.get('revision_suggestions', [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Review System"}

def start_gradio():
    """Start Gradio UI"""
    from app.ui.gradio_app import launch_ui
    launch_ui()

if __name__ == "__main__":
    # Start Gradio UI in background thread
    gradio_thread = threading.Thread(target=start_gradio, daemon=True)
    gradio_thread.start()
    
    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
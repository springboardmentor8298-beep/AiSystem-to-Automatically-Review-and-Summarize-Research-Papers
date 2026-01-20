## Baseline System (Non-AI / No Transformers)

This version of the project implements a complete classical NLP pipeline
without using deep learning or transformer-based models.

### Included
- Research paper retrieval (Semantic Scholar API)
- PDF download and text extraction
- Section-wise parsing of papers
- Extractive summarization (rule-based)
- Section-wise summarization
- Draft outline generation for literature review

### Excluded (Intentionally)
- Transformer-based models
- Large language models (LLMs)
- GPU or deep learning dependencies

This baseline ensures reproducibility, stability, and clarity before
introducing advanced AI-based methods in later milestones.


# AI Paper Summarizer — Day 1 & Day 2 Deliverables

## What I completed
1. Created Python virtual environment.
2. Added required folder structure for the project.
3. Created requirements.txt for dependency management.
4. Wrote environment check script (check_env.py) for PDF extraction test.

## How to run
<!-- .\venv\Scripts\activate
pip install -r requirements.txt
python scripts\check_env.py  -->

<!-- or -->

Use the Command Prompt instead of Power Shell

cd D:\paper-summarizer
.\venv\Scripts\activate.bat
python scripts\check_env.py

<!-- Verify Environment  -->
python scripts\check_env.py
<!-- Run the Functionality -->
python scripts\search_and_list.py --query "machine learning" --limit 5


<!-- I decided to build an ui after the day 3 task  -->

<!-- “I’m using SQLite initially because it’s lightweight, reliable, and ideal for prototyping. The schema is designed so it can later be migrated to a production database if needed.” -->

<!-- HTML/CSS/JS = Frontend
Python = Backend
They communicate via HTTP (fetch / API calls) -->

<!-- Browser (HTML/CSS/JS)
        ↓
Frontend Form (Query Input)
        ↓
Backend API (Python - Flask)
        ↓
Semantic Scholar Search
        ↓
Metadata JSON
        ↓
(UI shows results)
 -->


<!-- to run the backend  -->
python backend\app.py





<!-- “I implemented automated PDF downloading and text extraction using Python, storing both raw PDFs and extracted text for downstream summarization.” -->
Extracted text → Chunking → Summarization → Final output

## Abstractive Summarization (Optional)

The system supports optional Transformer-based abstractive summarization
using lightweight models (t5-small). If Transformers or Torch are not
available, the system automatically falls back to extractive summarization,
ensuring robustness and uninterrupted functionality.





# AI Research Paper Reviewer & Generator

## Overview

This project is an end-to-end AI system that automatically retrieves research papers,
extracts and analyzes their content, generates structured academic drafts,
and performs review and refinement through a polished UI.

The system is implemented in a milestone-driven architecture to ensure
clarity, modularity, and academic rigor.

---

## Milestone Structure

### Milestone 1 – Paper Retrieval

- Automated search using Semantic Scholar API
- PDF download based on topic
- Metadata dataset creation

File:

- milestone1_retrieval.py

---

### Milestone 2 – Text Extraction & Analysis

- PDF text extraction
- Section-wise parsing
- Key findings extraction and cross-paper comparison

File:

- milestone2_extraction_analysis.py

---

### Milestone 3 – Draft Generation (LLM-based)

- Abstract, Methods, Results generation
- Multi-paper synthesis
- APA-style reference formatting
- Implemented using Hugging Face models

File:

- milestone3_drafting_hf.py

---

### Milestone 4 – Review, Refinement & UI

- Automated critique and revision cycle
- Quality evaluation
- Final Gradio-based user interface
- Complete research report generation

File:

- milestone4_review_ui.py

---

## How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

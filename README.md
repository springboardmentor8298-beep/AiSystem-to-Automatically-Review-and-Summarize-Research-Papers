AI System to Automatically Review and Summarize Research Papers

This project is an AI-based research assistant developed as part of my internship.
The goal of the system is to automatically search research papers for a given topic, extract important content, summarize it using AI models, and generate a refined research draft through a simple user interface.

Through this project, I learned how to apply my programming knowledge to real-world problems and how AI systems are built end-to-end.


---

Project Description

Manually reading multiple research papers is time-consuming and inefficient.
This system automates the process by retrieving open-access research papers from the internet, extracting text directly from their online PDFs, summarizing key sections, and generating a structured research summary.

Initially, the system downloaded PDFs locally. Later, the architecture was improved to process PDFs directly from URLs without permanently storing them, making the solution more scalable and industry-ready.


---

Key Features

Topic-based research paper retrieval

Open-access paper filtering

URL-based PDF processing (no permanent PDF downloads)

Text extraction using PyMuPDF

AI-based summarization using HuggingFace models

Structured research draft generation

Automatic review and refinement

User-friendly Gradio interface



---

Technologies Used

Programming Language: Python

UI Framework: Gradio

PDF Processing: PyMuPDF (fitz)

AI / NLP: HuggingFace Transformers

API Handling: Requests

Environment Management: python-dotenv



---

Project Structure

AI-Research-Summarizer/
│
├── app/
│   ├── main.py                 # Main pipeline and Gradio UI
│   │
│   ├── modules/
│   │   ├── retrieval.py        # Research paper retrieval
│   │   ├── extract.py          # PDF text extraction from URLs
│   │   ├── analyze.py          # Summarization and analysis
│   │   ├── draft.py            # Research draft generation
│   │   └── review.py           # Draft review and refinement
│   │
│   ├── papers/
│   │   └── text/               # Temporarily stored extracted text
│   │
│   └── output/
│       ├── combined_abstracts.json
│       └── reviewed_research_draft.txt
│
├── requirements.txt
├── README.md
└── .env


---

How the System Works

1. The user enters a research topic in the UI


2. The system searches for open-access research papers online


3. PDF URLs are collected (without downloading files permanently)


4. Text is extracted directly from the PDF URLs


5. AI models summarize abstracts and results


6. A structured research draft is generated


7. The draft is reviewed and refined automatically


8. A final academic-style research summary is produced




---

Milestone Summary

Milestone 1 – Research Paper Retrieval

Topic-based search implemented

Open-access paper filtering

Shifted from local PDF downloads to URL-based access


Milestone 2 – Text Extraction and Analysis

Extracted text directly from online PDFs

Identified abstracts and results sections

AI-based summarization implemented


Milestone 3 – Research Draft Generation

Combined summaries from multiple papers

Generated a structured research draft

Stored intermediate results in JSON format


Milestone 4 – Review, UI, and Final Output

Automated review and refinement of the draft

Integrated the entire pipeline into a Gradio UI

Generated a final reviewed research report

Tested the pipeline with multiple topics



---

How to Run the Project

1. Create and activate a virtual environment


2. Install dependencies using:

pip install -r requirements.txt


3. Add your HuggingFace API key in a .env file


4. Run the application:

python app/main.py


5. Open the local URL shown in the terminal to access the UI




---

Output

combined_abstracts.json – Consolidated summaries of all papers

reviewed_research_draft.txt – Final reviewed research summary



---

Learning Outcome

As a Java developer, working with Python and AI models was new to me.
This project helped me understand how AI pipelines work in practice, how to integrate APIs, process real-world data, and build scalable systems.
The hands-on approach made complex AI concepts easy to understand and apply.


---

Conclusion

This project successfully demonstrates an end-to-end AI research assistant system.
It reflects real-world application of AI, automation, and software engineering principles and meets all the internship milestone requirements.


 

# 🧠 AI Research Paper Explorer

An AI-powered web application that automatically searches, reviews, and summarizes research papers for a given topic. The system retrieves open-access papers, extracts content from PDFs, and generates clean, human-readable summaries using NLP techniques.

---

## 🚀 Features

* 🔍 Topic-based research paper search
* 📄 Open-access PDF filtering
* 🧠 AI-based summarization (abstractive + extractive)
* 📑 Section-wise summaries (Abstract, Introduction, Conclusion)
* 📌 Overall topic summary across multiple papers
* ✍️ Spell correction for search queries
* 🎨 Clean, responsive web interface

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask, Semantic Scholar API
* **AI/NLP:** Hugging Face Transformers, custom extractive summarization
* **PDF Processing:** pdfplumber
* **Frontend:** HTML, CSS, JavaScript

---

## ⚙️ How It Works

1. User enters a research topic
2. System fetches relevant open-access papers
3. PDFs are processed directly from URLs
4. Text is cleaned and summarized using AI
5. Results are displayed in a structured, readable UI

---

## ▶️ Run Locally

```bash
pip install -r requirements.txt
python backend/app.py
```

Open: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🎓 Learning Outcome

This project demonstrates an end-to-end AI research assistant, covering real-world PDF processing, NLP summarization, backend API design, and frontend integration.

---

**Author:** Vivek Reddy
**Project Type:** Internship Project



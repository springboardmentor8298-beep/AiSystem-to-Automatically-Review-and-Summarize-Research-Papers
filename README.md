# 📄 Research Paper Summarizer

An AI-powered web application that searches academic literature and automatically generates a structured research paper draft including **Abstract, Introduction, Methods, Conclusion, and References** based on a given topic.

Built using **Streamlit**, **Semantic Scholar API**, and **Google Gemini (Generative AI)**.

## 🚀 Features

- 🔍 Search research papers by topic using Semantic Scholar
- 📚 Select number of papers to include (3, 5, 10, 15)
- ✍️ Automatically generates:
  - Abstract  
  - Introduction  
  - Methods (Survey / Conceptual)  
  - Conclusion  
  - References (paper titles)
- 🧠 Academic writing style
- 🌐 Clean, responsive Streamlit UI
- 🔐 Secure API key handling using `.env`

--

## 🛠️ Tech Stack

- **Frontend / UI**: Streamlit  
- **APIs**:
  - Semantic Scholar Graph API
  - Google Gemini API  
- **Backend / Logic**: Python  
- **Environment Management**: `python-dotenv`

---

## 📂 Project Structure
RESEARCH PAPER/
├── app.py # Main Streamlit application
├── .env # Environment variables (API keys)
├── .gitignore # Git ignore rules
├── dataset.json # Generated dataset (if used)
├── papers/ # Downloaded research papers (PDFs)

import os
from dotenv import load_dotenv

# Force load .env with override
load_dotenv(override=True)

class Config:
    # Debug: Print what's being loaded
    print("=" * 50)
    print("📁 LOADING CONFIGURATION")
    print("=" * 50)
    
    # Semantic Scholar API Key - MOST IMPORTANT
    S2_API_KEY = os.getenv("S2_API_KEY")
    print(f"🔑 S2_API_KEY: {'✅ LOADED' if S2_API_KEY else '❌ MISSING!'}")
    if S2_API_KEY:
        print(f"   First 10 chars: {S2_API_KEY[:10]}...")
    else:
        print(f"   ⚠️ Check your .env file - S2_API_KEY is not set!")
    
    # OpenAI/GPT4All settings
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "http://localhost:4891/v1")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "not-needed")
    
    # GPT Model - Fixed (was defined twice)
    GPT_MODEL = os.getenv("GPT_MODEL", "Llama 3.2 3B Instruct")
    print(f"🤖 GPT_MODEL: {GPT_MODEL}")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/paper_review")
    
    # System settings
    MAX_PAPERS = int(os.getenv("MAX_PAPERS", "3"))
    ABSTRACT_WORD_LIMIT = int(os.getenv("ABSTRACT_WORD_LIMIT", "100"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # API Endpoints
    SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"
    
    # Directory settings
    PDF_STORAGE = "storage/pdfs"
    EXTRACTED_TEXT_STORAGE = "storage/extracted"
    
    print("=" * 50)
    print("✅ Configuration loaded")
    print("=" * 50)
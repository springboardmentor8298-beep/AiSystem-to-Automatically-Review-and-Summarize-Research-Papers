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


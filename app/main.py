from dotenv import load_dotenv
import gradio as gr

from modules.retrieval import download_papers
from modules.extract import extract_all_papers
from modules.analyze import analyze_all
from modules.draft import generate_draft
from modules.review import review_draft

load_dotenv()


def full_pipeline(topic):
    """
    Runs the complete AI research summarization pipeline.
    """
    try:
        if not topic or not topic.strip():
            return "❌ Please enter a research topic."

        print(f"\n🔍 USER SELECTED TOPIC → {topic}")

        # Step 1: Retrieve paper URLs + metadata
        print("📥 Fetching research papers...")
        papers= download_papers(topic)

        if not papers:
            return "❌ No open-access papers found."

        # Step 2: Extract text from PDFs
        print("📄 Extracting paper content...")
        extract_all_papers(papers)

        # Step 3: Analyze papers (summary + metadata)
        print("🧠 Analyzing papers...")
        analyze_all()

        # Step 4: Generate structured draft
        print("📝 Generating draft...")
        draft = generate_draft()

        # Step 5: Review & refine
        print("🤖 Reviewing draft...")
        reviewed = review_draft(draft)

        print("✅ Pipeline Completed Successfully!")
        return reviewed

    except Exception as e:
        return f"❌ Pipeline Error: {e}"


def launch_app():
    with gr.Blocks() as demo:
        gr.Markdown("## 🧠 AI Research Paper Summarizer")

        gr.Markdown("""
        **Pipeline Flow**
        1. Topic-based paper retrieval  
        2. PDF URL processing (no local downloads)  
        3. Text extraction  
        4. AI-based summarization  
        5. Structured draft generation  
        6. Academic review  
        """)

        topic_input = gr.Textbox(
            label="Enter Research Topic",
            placeholder="Example: Deep Learning in Healthcare"
        )

        output_box = gr.Textbox(
            label="Final Reviewed Research Draft",
            lines=30
        )

        run_btn = gr.Button("Run Pipeline 🚀")

        run_btn.click(
            fn=full_pipeline,
            inputs=topic_input,
            outputs=output_box
        )

    demo.launch()


if __name__ == "__main__":
    launch_app()
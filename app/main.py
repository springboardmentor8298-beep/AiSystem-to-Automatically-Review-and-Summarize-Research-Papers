from dotenv import load_dotenv
import gradio as gr

from modules.retrieval import download_papers
from modules.extract import extract_all_papers
from modules.analyze import analyze_all
from modules.draft import generate_draft
from modules.review import review_draft

load_dotenv()


def full_pipeline(topic, progress=gr.Progress()):
    if not topic.strip():
        return "❌ Please enter a research topic."

    progress(0.1, desc="🔍 Understanding topic...")
    print(f"\nUSER SELECTED TOPIC → {topic}")

    progress(0.25, desc="📥 Fetching research papers...")
    papers = download_papers(topic)
    if not papers:
        return "❌ No open-access papers found."

    progress(0.45, desc="📄 Extracting paper content...")
    extract_all_papers(papers)

    progress(0.65, desc="🧠 Analyzing & summarizing papers...")
    analyze_all()

    progress(0.85, desc="📝 Generating structured draft...")
    draft = generate_draft()

    progress(0.95, desc="🤖 Reviewing & refining draft...")
    reviewed = review_draft(draft)

    progress(1.0, desc="✅ Completed")
    return reviewed


def launch_app():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:

        gr.Markdown("""
        # 🧠 AI Research Paper Summarizer  
        ### Automatically fetch, analyze, and summarize research papers using AI

        **How it works:**  
        1️⃣ Enter a research topic  
        2️⃣ System fetches open-access papers  
        3️⃣ AI summarizes key insights  
        4️⃣ Final reviewed draft is generated  
        """)

        with gr.Row():
            topic_input = gr.Textbox(
                label="📌 Research Topic",
                placeholder="Example: Deep Learning in Healthcare",
                lines=1
            )

        run_btn = gr.Button("🚀 Run Analysis", variant="primary")

        output_box = gr.Textbox(
            label="📄 Final Reviewed Research Draft",
            lines=25,
            interactive=False
        )

        run_btn.click(
            fn=full_pipeline,
            inputs=topic_input,
            outputs=output_box
        )

        gr.Markdown("""
        ---
        🔒 *Only open-access research papers are used.*  
        ⚡ *No PDFs are stored permanently — URL-based processing for efficiency.*
        """)

    demo.launch()


if __name__ == "__main__":
    launch_app()
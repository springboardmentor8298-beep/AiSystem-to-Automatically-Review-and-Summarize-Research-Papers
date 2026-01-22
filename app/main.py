from dotenv import load_dotenv
import gradio as gr

from modules.retrieval import download_papers
from modules.extract import extract_all_papers
from modules.analyze import analyze_all
from modules.draft import generate_draft
from modules.review import review_draft

load_dotenv()


def full_pipeline(topic, paper_count, progress=gr.Progress()):
    if not topic.strip():
        return "<p style='color:red;'>❌ Please enter a valid research topic.</p>"

    progress(0.1, desc="🔍 Understanding topic...")
    print(f"\nUSER SELECTED TOPIC → {topic}")
    print(f"NUMBER OF PAPERS → {paper_count}")

    progress(0.25, desc="📥 Fetching open-access research papers...")
    papers = download_papers(topic, limit=paper_count)
    if not papers:
        return "<p style='color:red;'>❌ No open-access papers found.</p>"

    progress(0.45, desc="📄 Extracting paper content...")
    extract_all_papers(papers)

    progress(0.65, desc="🧠 Analyzing & summarizing papers...")
    analyze_all()

    progress(0.85, desc="📝 Generating professional research draft...")
    draft = generate_draft()

    progress(0.95, desc="🤖 Reviewing & refining output...")
    reviewed = review_draft(draft)

    progress(1.0, desc="✅ Completed")

    # Render as clean HTML instead of markdown-style text
    html_output = reviewed.replace("\n", "<br>")
    return f"<div style='font-family:Arial; line-height:1.6;'>{html_output}</div>"


def launch_app():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:

        gr.Markdown("""
        <h1>🧠 AI Research Paper Summarizer</h1>
        <p style="font-size:16px;">
        Automatically fetch, analyze, and summarize open-access research papers using AI.
        </p>

        <h3>How it works</h3>
        <ol>
          <li>Enter a research topic</li>
          <li>Select number of papers</li>
          <li>System fetches open-access papers</li>
          <li>AI summarizes and generates a reviewed draft</li>
        </ol>
        """)

        with gr.Row():
            topic_input = gr.Textbox(
                label="📌 Research Topic",
                placeholder="Example: Explainable Artificial Intelligence",
                lines=1
            )

            paper_count = gr.Slider(
                minimum=1,
                maximum=10,
                step=1,
                value=3,
                label="📄 Number of Papers"
            )

        run_btn = gr.Button("🚀 Run Analysis", variant="primary")

        output_box = gr.HTML(
            label="📘 Final Reviewed Research Draft"
        )

        run_btn.click(
            fn=full_pipeline,
            inputs=[topic_input, paper_count],
            outputs=output_box
        )

        gr.Markdown("""
        <hr>
        <p style="font-size:14px;">
        🔒 Only open-access research papers are used.<br>
        ⚡ PDFs are not downloaded or stored — processing is done via URLs to reduce storage usage.
        </p>
        """)

    demo.launch(
        share=True,
        server_port=7860
    )


if __name__ == "__main__":
    launch_app()
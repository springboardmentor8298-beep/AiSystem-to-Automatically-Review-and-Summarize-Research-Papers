import gradio as gr
import os
import subprocess

BASE_DIR = "generated_review"

# ---------- PIPELINE RUNNER ----------
def run_full_pipeline(topic):
    if not topic:
        return "⚠ Please enter a topic."

    topic = topic.strip()

    try:
        # Data collection & preprocessing
        subprocess.run(["python", "semantic_scholar_api.py", topic], check=True)
        subprocess.run(["python", "scripts/pdf_text_extractor.py", topic], check=True)
        subprocess.run(["python", "scripts/section_extractor.py", topic], check=True)
        subprocess.run(["python", "scripts/keyword_extractor.py", topic], check=True)

        # 🔥 FAST: generate Abstract + Methods + Results in ONE run
        subprocess.run(
            ["python", "generation/generate_all_sections.py", topic],
            check=True
        )

        # References + Final report
        subprocess.run(["python", "generation/references_generator.py", topic], check=True)
        subprocess.run(["python", "generation/final_report_generator.py", topic], check=True)

        return "✅ Full review generated successfully (optimized pipeline)."

    except subprocess.CalledProcessError as e:
        return f"❌ Pipeline failed: {e}"


# ---------- FILE LOADER ----------
def load_section(topic, section):
    topic = topic.strip().replace(" ", "_").lower()

    file_map = {
        "abstract": "abstract.txt",
        "methods": "methods.txt",
        "results": "results.txt",
        "references": "references.txt",
        "final_report": "final_report.txt",
    }

    path = os.path.join(BASE_DIR, topic, file_map[section])

    if not os.path.exists(path):
        return f"❌ {section} not found. Please generate first."

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ---------- UI ----------
with gr.Blocks() as demo:
    gr.Markdown("""
    # 📄 AI System to Automatically Review and Summarize Research Papers

    Enter a research topic and generate a complete AI-powered literature review
    using Semantic Scholar and Hugging Face models.
    """)

    topic_input = gr.Textbox(
        label="Research Topic",
        placeholder="e.g., Instagram, Speech Recognition, Data Science"
    )

    generate_btn = gr.Button("🚀 Generate Review")
    status = gr.Textbox(label="Status")

    generate_btn.click(run_full_pipeline, topic_input, status)

    with gr.Row():
        abstract_btn = gr.Button("📌 Abstract")
        methods_btn = gr.Button("🧪 Methods")
        results_btn = gr.Button("📊 Results")
        refs_btn = gr.Button("📚 References")
        final_btn = gr.Button("📑 Final Report")

    output = gr.Textbox(lines=22, label="Generated Content")

    abstract_btn.click(load_section, [topic_input, gr.State("abstract")], output)
    methods_btn.click(load_section, [topic_input, gr.State("methods")], output)
    results_btn.click(load_section, [topic_input, gr.State("results")], output)
    refs_btn.click(load_section, [topic_input, gr.State("references")], output)
    final_btn.click(load_section, [topic_input, gr.State("final_report")], output)

demo.launch()

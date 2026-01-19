import gradio as gr
import subprocess
import os
import sys
import shutil

BASE_DIR = "data/generated/final"

SECTIONS = ["abstract", "introduction", "method", "results", "conclusion", "references"]

# ✅ Always use the SAME Python as the running venv
PYTHON = sys.executable


# 🔁 RESET OLD DATA BEFORE NEW TOPIC
def reset_previous_run():
    folders = [
        "data/pdfs",
        "data/extracted_text",
        "data/sections",
        "data/generated"
    ]

    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)


def run_pipeline(topic):
    if not topic.strip():
        return "❌ Please enter a valid topic."

    # ✅ clear old topic data
    reset_previous_run()

    commands = [
        [PYTHON, "scripts/search_and_list.py", topic, "--n", "5"],
        [PYTHON, "scripts/pdf_downloader.py"],          # ✅ THIS WAS MISSING
        [PYTHON, "scripts/extract_text.py"],
        [PYTHON, "scripts/extract_sections.py"],
        [PYTHON, "scripts/group_sections.py"],
        [PYTHON, "scripts/generate_sections.py"],
        [PYTHON, "scripts/generate_references.py"],
    ]

    try:
        for cmd in commands:
            subprocess.run(
                cmd,
                check=True,
                cwd=os.getcwd()
            )

        return f"✅ Pipeline completed successfully for topic: {topic}"

    except subprocess.CalledProcessError as e:
        return f"❌ Error during execution: {e}"

    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


def load_section(section):
    path = os.path.join(BASE_DIR, f"{section}.txt")

    if not os.path.exists(path):
        return "❌ Section not found. Please run pipeline first."

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_section(section, text):
    path = os.path.join(BASE_DIR, f"{section}.txt")

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    return "✅ Saved successfully."


with gr.Blocks() as app:
    gr.Markdown("# 🧠 Automated Research Paper Generator")

    with gr.Tab("1️⃣ Topic Selection"):
        topic_input = gr.Textbox(
            label="Enter Research Topic",
            placeholder="e.g., Machine Learning"
        )

        run_btn = gr.Button("Run Full Pipeline")

        status = gr.Textbox(
            label="Status",
            interactive=False
        )

        run_btn.click(run_pipeline, inputs=topic_input, outputs=status)

    with gr.Tab("2️⃣ Review & Edit"):
        section_dd = gr.Dropdown(SECTIONS, label="Select Section")

        content_box = gr.Textbox(
            lines=20,
            label="Section Content"
        )

        load_btn = gr.Button("Load")
        save_btn = gr.Button("Save")

        load_btn.click(load_section, inputs=section_dd, outputs=content_box)
        save_btn.click(save_section, inputs=[section_dd, content_box], outputs=None)

app.launch()

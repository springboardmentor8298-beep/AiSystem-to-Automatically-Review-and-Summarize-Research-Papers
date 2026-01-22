import json
import gradio as gr
from transformers import pipeline

# =========================
# CONFIG
# =========================
MODEL_NAME = "google/flan-t5-base"
DRAFT_FILE = "draft_output/final_draft.json"

# =========================
# LOAD MODEL
# =========================
print("[INFO] Loading Hugging Face model...")
generator = pipeline(
    "text2text-generation",
    model=MODEL_NAME,
    max_length=512
)

# =========================
# LOAD DRAFT
# =========================
def load_draft():
    with open(DRAFT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

draft = load_draft()

# =========================
# REVIEW LOGIC
# =========================
def critique_section(text, section_name):
    prompt = f"""
Critically review the following {section_name} section.
Identify weaknesses, missing elements, and clarity issues.
Provide concise improvement suggestions.

{text}
"""
    return generator(prompt)[0]["generated_text"]

def revise_section(text, feedback, section_name):
    prompt = f"""
Revise the following {section_name} section using the given feedback.

SECTION:
{text}

FEEDBACK:
{feedback}
"""
    return generator(prompt)[0]["generated_text"]

# =========================
# UI CALLBACK
# =========================
def run_review_cycle():
    abstract = draft["abstract"]
    methods = draft["methods"]
    results = draft["results"]

    abstract_feedback = critique_section(abstract, "Abstract")
    methods_feedback = critique_section(methods, "Methods")
    results_feedback = critique_section(results, "Results")

    revised_abstract = revise_section(abstract, abstract_feedback, "Abstract")
    revised_methods = revise_section(methods, methods_feedback, "Methods")
    revised_results = revise_section(results, results_feedback, "Results")

    final_report = f"""
ABSTRACT
{revised_abstract}

METHODS
{revised_methods}

RESULTS
{revised_results}

REFERENCES
""" + "\n".join(draft["references"])

    return (
        revised_abstract,
        revised_methods,
        revised_results,
        final_report
    )

# =========================
# GRADIO UI
# =========================
with gr.Blocks(title="AI Research Paper Reviewer & Refiner") as demo:
    gr.Markdown("## 🧠 AI Research Paper Review & Refinement System")
    gr.Markdown(
        "This interface allows automated critique, revision, and final synthesis "
        "of research paper sections generated in previous milestones."
    )

    with gr.Tab("Original Draft"):
        gr.Textbox(draft["abstract"], label="Abstract", lines=10)
        gr.Textbox(draft["methods"], label="Methods", lines=10)
        gr.Textbox(draft["results"], label="Results", lines=10)

    with gr.Tab("Refined Output"):
        revised_abstract = gr.Textbox(label="Revised Abstract", lines=10)
        revised_methods = gr.Textbox(label="Revised Methods", lines=10)
        revised_results = gr.Textbox(label="Revised Results", lines=10)

    with gr.Tab("Final Report"):
        final_report_box = gr.Textbox(label="Complete Research Report", lines=25)

    critique_btn = gr.Button("🔍 Critique & Revise")

    critique_btn.click(
        fn=run_review_cycle,
        outputs=[
            revised_abstract,
            revised_methods,
            revised_results,
            final_report_box
        ]
    )

demo.launch()

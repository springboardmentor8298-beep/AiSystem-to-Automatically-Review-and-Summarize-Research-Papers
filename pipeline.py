import os
from semantic_scholar_api import fetch_and_download_papers
from scripts.pdf_text_extractor import extract_raw_text
from scripts.section_extractor import extract_sections
from generation.abstract_generator import generate_abstract
from generation.methods_generator import generate_methods
from generation.results_generator import generate_results
from generation.references_generator import generate_references


def run_pipeline(topic):
    """
    Full automated research paper review pipeline
    """

    # ----------------------------
    # Input safety
    # ----------------------------
    if isinstance(topic, dict):
        topic = topic.get("value") or topic.get("label") or ""

    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("Invalid topic input")

    topic_clean = topic.strip().replace(" ", "_").lower()
    output_dir = f"generated_review/{topic_clean}"
    os.makedirs(output_dir, exist_ok=True)

    # ----------------------------
    # Step 1: Download papers
    # ----------------------------
    fetch_and_download_papers(topic)

    # ----------------------------
    # Step 2: Extract raw text
    # ----------------------------
    extract_raw_text(topic)

    # ----------------------------
    # Step 3: Extract sections
    # ----------------------------
    extract_sections(topic)

    # ----------------------------
    # Step 4: Generate review sections
    # ----------------------------
    abstract = generate_abstract(topic)
    methods = generate_methods(topic)
    results = generate_results(topic)
    references = generate_references(topic)

    # ----------------------------
    # Step 5: Save outputs
    # ----------------------------
    with open(f"{output_dir}/abstract.txt", "w", encoding="utf-8") as f:
        f.write(abstract)

    with open(f"{output_dir}/methods.txt", "w", encoding="utf-8") as f:
        f.write(methods)

    with open(f"{output_dir}/results.txt", "w", encoding="utf-8") as f:
        f.write(results)

    with open(f"{output_dir}/references.txt", "w", encoding="utf-8") as f:
        f.write(references)

    print(f"✅ Pipeline completed successfully for topic: {topic_clean}")
    return True

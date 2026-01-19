def critique(text):
    comments = []
    if len(text) < 500:
        comments.append("Content is too short; consider expanding.")
    if "figure" in text.lower():
        comments.append("Ensure all figures are referenced properly.")
    if "conclusion" not in text.lower():
        comments.append("Conclusion section could be strengthened.")
    return "\n".join(comments) or "No major issues found."

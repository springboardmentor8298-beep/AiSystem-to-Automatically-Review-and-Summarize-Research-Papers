from transformers import pipeline

# Lightweight & fast model (CPU-friendly)
generator = pipeline(
    "text-generation",
    model="distilgpt2",
    device=-1  # force CPU
)

def generate_text(prompt, max_new_tokens=120):
    """
    Generate text safely regardless of prompt length
    """
    output = generator(
        prompt,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=0.6,
        num_return_sequences=1
    )
    return output[0]["generated_text"]

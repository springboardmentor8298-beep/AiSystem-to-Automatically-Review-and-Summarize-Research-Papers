import re

# ---------------------------------------
# SECTION HEADERS (STRICT + ORDERED)
# ---------------------------------------
SECTION_PATTERNS = [
    ("abstract", r"\babstract\b"),
    ("introduction", r"\bintroduction\b"),
    ("methods", r"\b(methods?|methodology)\b"),
    ("results", r"\b(results?|experiments?)\b"),
    ("discussion", r"\bdiscussion\b"),
    ("conclusion", r"\b(conclusion|conclusions)\b"),
]

# ---------------------------------------
# CLEAN SECTION TEXT
# ---------------------------------------
def clean_section(text: str) -> str:
    if not text:
        return ""

    # Remove URLs
    text = re.sub(r"http\S+", "", text)

    # Remove figure / table captions
    text = re.sub(
        r"\b(fig(ure)?|table)\s*\d+.*",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove references leakage
    text = re.split(
        r"\breferences\b|\bbibliography\b",
        text,
        flags=re.IGNORECASE
    )[0]

    # Fix broken spacing
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# ---------------------------------------
# QUALITY CHECK (CRITICAL)
# ---------------------------------------
def is_valid_section(text: str) -> bool:
    """
    Ensures section is academically meaningful
    """
    if not text:
        return False

    # Minimum length
    if len(text) < 500:
        return False

    # Must have multiple sentences
    if text.count(".") < 3:
        return False

    return True


# ---------------------------------------
# SECTION PARSER (FINAL)
# ---------------------------------------
def parse_sections(text: str) -> dict:
    """
    Extracts only high-quality semantic sections
    """
    if not text or len(text) < 1000:
        return {}

    sections = {}
    lower_text = text.lower()

    matches = []

    for name, pattern in SECTION_PATTERNS:
        match = re.search(pattern, lower_text)
        if match:
            matches.append((match.start(), name))

    if not matches:
        return {}

    matches.sort()

    for i, (start, name) in enumerate(matches):
        end = matches[i + 1][0] if i + 1 < len(matches) else len(text)

        raw = text[start:end]
        cleaned = clean_section(raw)

        if is_valid_section(cleaned):
            sections[name] = cleaned

    return sections

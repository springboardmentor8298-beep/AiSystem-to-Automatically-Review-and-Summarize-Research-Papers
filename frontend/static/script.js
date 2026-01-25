// -------------------------
// TOGGLE LABEL
// -------------------------
function updateToggleLabel() {
    const toggle = document.getElementById("summaryToggle");
    const label = document.getElementById("toggleText");
    if (!label) return;

    if (toggle.checked) {
        label.textContent = "📄 Full Paper Mode";
        label.style.color = "#059669";
    } else {
        label.textContent = "🧠 Abstract Mode";
        label.style.color = "#2563eb";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    updateToggleLabel();
    const toggle = document.getElementById("summaryToggle");
    if (toggle) toggle.addEventListener("change", updateToggleLabel);
});

// -------------------------
// MODE CHECK
// -------------------------
function isFullPaperMode() {
    return document.getElementById("summaryToggle").checked;
}

// -------------------------
// SEARCH PAPERS
// -------------------------
function searchPapers() {
    const query = document.getElementById("query").value.trim();
    const limit = document.getElementById("limit").value;
    const resultsDiv = document.getElementById("results");
    const loading = document.getElementById("loading");
    const overallCard = document.getElementById("overall-summary");
    const overallText = document.getElementById("overall-text");
    const searchBtn = document.getElementById("searchBtn");

    if (!query) {
        alert("Please enter a topic");
        return;
    }
   

    resultsDiv.innerHTML = "";
    overallCard.classList.add("hidden");
    loading.style.display = "block";

    searchBtn.disabled = true;
    searchBtn.innerHTML = `<span class="spinner"></span> Searching...`;

    fetch(`http://127.0.0.1:5000/search?query=${encodeURIComponent(query)}&limit=${limit}`)
        .then(res => res.json())
        .then(data => {
            loading.style.display = "none";

            if (data.overall_summary) {
                overallText.textContent = data.overall_summary;
                overallCard.classList.remove("hidden");
            }

            if (!data.papers || data.papers.length === 0) {
                resultsDiv.innerHTML = "<p>No accessible papers found.</p>";
                return;
            }

            data.papers.forEach(paper => {

    // 🔥 FILTER BASED ON MODE
    if (isFullPaperMode() && !paper.pdf_url) return;
    if (!isFullPaperMode() && !paper.abstract) return;

    const card = document.createElement("div");
    card.className = "paper card";

    const encodedAbstract = btoa(
        unescape(encodeURIComponent(paper.abstract || ""))
    );

    card.innerHTML = `
        <h3>${paper.title}</h3>
        <p class="meta">${paper.venue || "Unknown"} • ${paper.year || "N/A"}</p>

        <div class="links">
            ${paper.publisher_url ? `<a href="${paper.publisher_url}" target="_blank">Publisher</a>` : ""}
            ${paper.pdf_url ? `<a href="${paper.pdf_url}" target="_blank">PDF</a>` : ""}
        </div>

        <div class="actions">
            <button type="button" class="summary-btn">Summarize</button>
        </div>

        <div class="summary hidden"></div>
    `;

    const btn = card.querySelector(".summary-btn");
    const summaryDiv = card.querySelector(".summary");

    btn.addEventListener("click", () => {
        toggleSummary(encodedAbstract, paper.pdf_url || "", btn, summaryDiv);
    });

    resultsDiv.appendChild(card);
});



        })
        .catch(err => {
            loading.style.display = "none";
            resultsDiv.innerHTML = "<p>Error fetching results.</p>";
            console.error(err);
        })
        .finally(() => {
            searchBtn.disabled = false;
            searchBtn.textContent = "Search";
        });
}

// -------------------------
// SUMMARY TOGGLE (CORE)
// -------------------------
function toggleSummary(encodedAbstract, pdfUrl, btn, summaryDiv) {
    if (!summaryDiv.classList.contains("hidden")) {
        summaryDiv.classList.add("hidden");
        btn.textContent = "Summarize";
        btn.classList.remove("secondary");
        return;
    }

    if (summaryDiv.dataset.loaded === "true") {
        summaryDiv.classList.remove("hidden");
        btn.textContent = "Hide Summary";
        btn.classList.add("secondary");
        return;
    }

    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> Summarizing...`;
    summaryDiv.classList.remove("hidden");
    summaryDiv.innerHTML = `<div class="spinner"></div> Processing...`;

    if (isFullPaperMode()) {
        if (!pdfUrl) {
            summaryDiv.innerHTML = "❌ Full paper not available.";
            restoreButton(btn);
            return;
        }
        fetchFullPaper(pdfUrl, summaryDiv, btn);
    } else {
        fetchAbstract(encodedAbstract, summaryDiv, btn);
    }
}

// -------------------------
// ABSTRACT SUMMARY
// -------------------------
function fetchAbstract(encodedAbstract, summaryDiv, btn) {
    let abstract = "";
    try {
        abstract = decodeURIComponent(escape(atob(encodedAbstract)));
    } catch {
        summaryDiv.innerHTML = "Invalid abstract.";
        restoreButton(btn);
        return;
    }

    if (!abstract.trim()) {
        summaryDiv.innerHTML = "No abstract available.";
        restoreButton(btn);
        return;
    }

    fetch("http://127.0.0.1:5000/summarize_abstract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ abstract })
    })
        .then(res => res.json())
        .then(data => {
            summaryDiv.innerHTML = `
    <h4>Abstract Summary</h4>
    <p>${highlightKeywords(data.summary)}</p>
`;
            summaryDiv.dataset.loaded = "true";
            btn.textContent = "Hide Summary";
            btn.classList.add("secondary");
        })
        .catch(() => {
            summaryDiv.innerHTML = "Abstract summarization failed.";
        })
        .finally(() => restoreButton(btn, true));
}

// -------------------------
// FULL PAPER SUMMARY (TABS UI)
// -------------------------
function fetchFullPaper(pdfUrl, summaryDiv, btn) {
    fetch("http://127.0.0.1:5000/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pdf_url: pdfUrl })
    })
        .then(res => {
            if (!res.ok) {
                throw new Error("Failed to fetch summary");
            }
            return res.json();
        })
        .then(data => {
            const full = data.full || "Not available.";
            const abstract = data.abstract || "Not available.";
            const introduction = data.introduction || "Not available.";
            const conclusion = data.conclusion || "Not available.";

            summaryDiv.innerHTML = `
                <div class="tabs">
                    <button class="tab active" onclick="openTab(this, 'full')">
                        📘 Full Summary
                    </button>
                    <button class="tab" onclick="openTab(this, 'abstract')">
                        🧠 Abstract
                    </button>
                    <button class="tab" onclick="openTab(this, 'introduction')">
                        📖 Introduction
                    </button>
                    <button class="tab" onclick="openTab(this, 'conclusion')">
                        ✅ Conclusion
                    </button>
                </div>

                <div class="tab-content active" id="tab-full">
                    <div class="summary-text">
                        ${formatSummaryText(highlightKeywords(full))}
                    </div>
                </div>

                <div class="tab-content" id="tab-abstract">
                    <div class="summary-text">
                        ${formatSummaryText(highlightKeywords(abstract))}
                    </div>
                </div>

                <div class="tab-content" id="tab-introduction">
                    <div class="summary-text">
                        ${formatSummaryText(highlightKeywords(introduction))}
                    </div>
                </div>

                <div class="tab-content" id="tab-conclusion">
                    <div class="summary-text">
                        ${formatSummaryText(highlightKeywords(conclusion))}
                    </div>
                </div>
            `;

            summaryDiv.dataset.loaded = "true";
            btn.textContent = "Hide Summary";
            btn.classList.add("secondary");
        })
        .catch(err => {
            console.error(err);
            summaryDiv.innerHTML = `
                <p class="error-text">
                    ❌ Failed to generate full paper summary.
                </p>
            `;
        })
        .finally(() => {
            restoreButton(btn, true);
        });
}



// -------------------------
// TAB HANDLER
// -------------------------
function openTab(btn, section) {
    const container = btn.closest(".summary");

    container.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    container.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

    btn.classList.add("active");
    const tab = container.querySelector(`#tab-${section}`);
    if (tab) tab.classList.add("active");
}

// -------------------------


// -------------------------
// BUTTON RESTORE
// -------------------------
function restoreButton(btn, keepText = false) {
    btn.disabled = false;
    if (!keepText) btn.textContent = "Summarize";
}
// -------------------------
// SUMMARY FORMATTER
// -------------------------
function formatSummaryText(text) {
    if (!text || text.trim() === "" || text === "Not available.") {
        return `<p class="muted">Not available.</p>`;
    }

    // Split into sentences
    const sentences = text
        .replace(/\s+/g, " ")
        .split(/(?<=[.!?])\s+/);

    // Group sentences into paragraphs (3 per paragraph)
    let html = "";
    for (let i = 0; i < sentences.length; i += 3) {
        const chunk = sentences.slice(i, i + 3).join(" ");
        html += `<p>${chunk}</p>`;
    }

    return html;
}
// -------------------------
// KEYWORD HIGHLIGHTER
// -------------------------
function highlightKeywords(text) {
    if (!text) return "";

    const keywords = [
        "model", "approach", "method", "results",
        "performance", "dataset", "architecture",
        "training", "evaluation", "conclusion"
    ];

    let highlighted = text;

    keywords.forEach(word => {
        const regex = new RegExp(`\\b(${word})\\b`, "gi");
        highlighted = highlighted.replace(
            regex,
            `<span class="keyword">$1</span>`
        );
    });

    return highlighted;
}
// -------------------------
// KEYWORD HIGHLIGHTER
// -------------------------
const AI_KEYWORDS = [
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "neural network",
    "transformer",
    "attention",
    "large language model",
    "llm",
    "nlp",
    "natural language processing",
    "computer vision",
    "reinforcement learning",
    "self-supervised",
    "unsupervised",
    "supervised",
    "classification",
    "regression",
    "embedding",
    "fine-tuning",
    "pretraining",
    "dataset",
    "model",
    "architecture",
    "training",
    "evaluation",
    "accuracy",
    "loss",
    "optimizer",
    "gradient",
    "token",
    "sequence",
    "prediction"
];

// Highlight keywords safely (HTML-preserving)
function highlightKeywords(text) {
    if (!text || typeof text !== "string") return text;

    let highlighted = text;

    AI_KEYWORDS.forEach(keyword => {
        const regex = new RegExp(`\\b(${keyword})\\b`, "gi");
        highlighted = highlighted.replace(
            regex,
            `<span class="highlight-keyword">$1</span>`
        );
    });

    return highlighted;
}


// =========================
// TOGGLE LABEL
// =========================
function updateToggleLabel() {
    const toggle = document.getElementById("summaryToggle");
    const label = document.getElementById("toggleText");
    if (!label) return;

    if (toggle.checked) {
        label.textContent = "📄 Full Paper Mode";
        label.style.color = "#059669";
    } else {
        label.textContent = "🧠 Recommended: Abstract Mode";
        label.style.color = "#2563eb";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    updateToggleLabel();
    const toggle = document.getElementById("summaryToggle");
    if (toggle) toggle.addEventListener("change", updateToggleLabel);
});

// =========================
// MODE CHECK
// =========================
function isFullPaperMode() {
    return document.getElementById("summaryToggle").checked;
}

// =========================
// SEARCH PAPERS
// =========================
function searchPapers() {
    const query = document.getElementById("query").value.trim();
    const limit = document.getElementById("limit").value;
    const resultsDiv = document.getElementById("results");
    const loading = document.getElementById("loading");
    const overallCard = document.getElementById("overall-summary");
    const overallText = document.getElementById("overall-text");
    const searchBtn = document.getElementById("searchBtn");
    const spellHint = document.getElementById("spell-hint");

    if (!query) {
        alert("Please enter a topic");
        return;
    }

    resultsDiv.innerHTML = "";
    overallCard.classList.add("hidden");
    loading.classList.remove("hidden");
    spellHint?.classList.add("hidden");

    searchBtn.disabled = true;
    searchBtn.innerHTML = `<span class="spinner"></span> Searching...`;

    const mode = isFullPaperMode() ? "full" : "abstract";

    fetch(
        `http://127.0.0.1:5000/search?query=${encodeURIComponent(
            query
        )}&limit=${limit}&mode=${mode}`
    )
        .then(res => res.json())
        .then(data => {
            loading.classList.add("hidden");

            // 🔍 SPELLING HINT
            if (
                spellHint &&
                data.original_query &&
                data.query &&
                data.original_query.toLowerCase() !== data.query.toLowerCase()
            ) {
                spellHint.innerHTML = `Did you mean <span>${data.query}</span>?`;
                spellHint.classList.remove("hidden");
            }

            // 📌 OVERALL SUMMARY (ALWAYS)
            if (data.overall_summary && data.overall_summary.length > 80) {
                overallText.textContent = data.overall_summary;
                overallCard.classList.remove("hidden");
            }

            if (!data.papers || data.papers.length === 0) {
                resultsDiv.innerHTML = "<p>No suitable papers found.</p>";
                return;
            }

            data.papers.forEach(paper => {
                // ❌ SAFETY: Full paper mode must have PDF
                if (isFullPaperMode() && !paper.pdf_url) return;

                const card = document.createElement("div");
                card.className = "paper card";

                const encodedAbstract = btoa(
                    unescape(encodeURIComponent(paper.abstract || ""))
                );

                card.innerHTML = `
                    <h3>${paper.title}</h3>
                    <p class="meta">${paper.venue || "Unknown"} • ${paper.year || "N/A"}</p>

                    <div class="links">
                        ${paper.pdf_url ? `<a href="${paper.pdf_url}" target="_blank">PDF</a>` : ""}
                        ${paper.publisher_url ? `<a href="${paper.publisher_url}" target="_blank">Paper</a>` : ""}
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
        .catch(() => {
            loading.classList.add("hidden");
            resultsDiv.innerHTML = "<p>Error fetching results.</p>";
        })
        .finally(() => {
            searchBtn.disabled = false;
            searchBtn.textContent = "Search";
        });
}

// =========================
// SUMMARY TOGGLE
// =========================
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
        fetchFullPaper(pdfUrl, summaryDiv, btn);
    } else {
        fetchAbstract(encodedAbstract, summaryDiv, btn);
    }
}

// =========================
// ABSTRACT SUMMARY
// =========================
function fetchAbstract(encodedAbstract, summaryDiv, btn) {
    const abstract = decodeURIComponent(escape(atob(encodedAbstract)));

    fetch("http://127.0.0.1:5000/summarize_abstract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ abstract })
    })
        .then(res => res.json())
        .then(data => {
            summaryDiv.innerHTML = `
                <h4>Abstract Summary</h4>
                ${formatSummaryText(data.summary)}
            `;
            summaryDiv.dataset.loaded = "true";
            btn.textContent = "Hide Summary";
            btn.classList.add("secondary");
        })
        .finally(() => restoreButton(btn, true));
}

// =========================
// FULL PAPER SUMMARY (SECTION BUTTONS)
// =========================
function fetchFullPaper(pdfUrl, summaryDiv, btn) {
    fetch("http://127.0.0.1:5000/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pdf_url: pdfUrl })
    })
        .then(res => res.json())
        .then(data => {
            let buttonsHTML = "";
            let contentHTML = "";
            let first = true;

            ["abstract", "introduction", "conclusion"].forEach(key => {
                if (isValidSection(data[key])) {
                    buttonsHTML += `
                        <button class="tab ${first ? "active" : ""}" data-key="${key}">
                            ${key.charAt(0).toUpperCase() + key.slice(1)}
                        </button>
                    `;
                    contentHTML += `
                        <div class="tab-content ${first ? "active" : ""}" id="${key}">
                            ${formatSummaryText(data[key])}
                        </div>
                    `;
                    first = false;
                }
            });

            if (!buttonsHTML) {
                summaryDiv.innerHTML = "";
                restoreButton(btn);
                return;
            }

            summaryDiv.innerHTML = `
                <div class="tabs">${buttonsHTML}</div>
                ${contentHTML}
            `;

            attachTabHandlers(summaryDiv);
            summaryDiv.dataset.loaded = "true";
            btn.textContent = "Hide Summary";
            btn.classList.add("secondary");
        })
        .finally(() => restoreButton(btn, true));
}

// =========================
// HELPERS
// =========================
function isValidSection(text) {
    return text && text.trim().length >= 150;
}

function restoreButton(btn, keepText = false) {
    btn.disabled = false;
    if (!keepText) btn.textContent = "Summarize";
}

function formatSummaryText(text) {
    if (!text) return "";
    const sentences = text.split(/(?<=[.!?])\s+/);
    let html = "";
    for (let i = 0; i < sentences.length; i += 3) {
        html += `<p>${sentences.slice(i, i + 3).join(" ")}</p>`;
    }
    return html;
}

function attachTabHandlers(container) {
    const tabs = container.querySelectorAll(".tab");
    const contents = container.querySelectorAll(".tab-content");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            contents.forEach(c => c.classList.remove("active"));
            tab.classList.add("active");
            container
                .querySelector(`#${tab.dataset.key}`)
                .classList.add("active");
        });
    });
}

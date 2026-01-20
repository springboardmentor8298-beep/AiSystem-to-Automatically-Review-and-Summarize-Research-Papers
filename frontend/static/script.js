function getSummaryMode() {
    return document.querySelector('input[name="summaryMode"]:checked').value;
}

function searchPapers() {
    const query = document.getElementById("query").value.trim();
    const limit = document.getElementById("limit").value;
    const resultsDiv = document.getElementById("results");
    const loading = document.getElementById("loading");

    resultsDiv.innerHTML = "";
    loading.style.display = "block";

    fetch(`http://127.0.0.1:5000/search?query=${encodeURIComponent(query)}&limit=${limit}`)
        .then(res => res.json())
        .then(result => {
            loading.style.display = "none";

            const papers = Array.isArray(result) ? result : result.data;

            if (!papers || papers.length === 0) {
                resultsDiv.innerHTML = "<p>No results found.</p>";
                return;
            }

            const mode = getSummaryMode();

            papers.forEach(paper => {
                const div = document.createElement("div");
                div.className = "paper";

                const encodedAbstract = paper.abstract
                    ? btoa(unescape(encodeURIComponent(paper.abstract)))
                    : null;

                let actionButton = "";

                if (mode === "abstract") {
                    actionButton = encodedAbstract
                        ? `<button onclick="summarizeAbstract('${encodedAbstract}', this)">
                              Summarize Abstract
                           </button>`
                        : `<p><i>No abstract available</i></p>`;
                } else {
                    actionButton = paper.openAccessPdf?.url
                        ? `<button onclick="downloadAndSummarize('${paper.openAccessPdf.url}', this)">
                              Download PDF & Summarize
                           </button>`
                        : `<p><i>No open-access PDF</i></p>`;
                }

                div.innerHTML = `
                    <h3>${paper.title}</h3>
                    <p><b>Year:</b> ${paper.year || "N/A"}</p>
                    ${actionButton}
                    <div class="summary"></div>
                `;

                resultsDiv.appendChild(div);
            });
        })
        .catch(err => {
            loading.style.display = "none";
            resultsDiv.innerHTML = "<p>Error fetching results.</p>";
            console.error(err);
        });
}


// ---------------- ABSTRACT ----------------
function summarizeAbstract(encodedAbstract, btn) {
    const summaryDiv = btn.parentElement.querySelector(".summary");
    summaryDiv.innerHTML = "<p>Summarizing abstract...</p>";

    let abstract = "";
    try {
        abstract = decodeURIComponent(escape(atob(encodedAbstract)));
    } catch {
        summaryDiv.innerHTML = "Invalid abstract data.";
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
                <p>${data.summary || "Failed to summarize."}</p>
            `;
        })
        .catch(() => {
            summaryDiv.innerHTML = "Abstract summarization failed.";
        });
}


// ---------------- FULL PAPER ----------------
function downloadAndSummarize(pdfUrl, btn) {
    const summaryDiv = btn.parentElement.querySelector(".summary");
    summaryDiv.innerHTML = "<p>Downloading PDF and summarizing...</p>";

    fetch("http://127.0.0.1:5000/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pdf_url: pdfUrl })
    })
        .then(res => res.json())
        .then(data => {
            summaryDiv.innerHTML = `
                <h4>Full Paper Summary</h4>
                <p>${data.summary || "Failed to summarize PDF."}</p>
            `;
        })
        .catch(() => {
            summaryDiv.innerHTML = "PDF summarization failed.";
        });
}

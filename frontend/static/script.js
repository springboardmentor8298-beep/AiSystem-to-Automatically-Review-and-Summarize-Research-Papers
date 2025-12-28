function searchPapers() {
    const query = document.getElementById("query").value;
    const limit = document.getElementById("limit").value;
    const resultsDiv = document.getElementById("results");
    const loading = document.getElementById("loading");

    resultsDiv.innerHTML = "";
    loading.style.display = "block";

    fetch(`http://127.0.0.1:5000/search?query=${query}&limit=${limit}`)
        .then(response => response.json())
        .then(data => {
            loading.style.display = "none";

            if (data.length === 0) {
    resultsDiv.innerHTML = `
        <p>No papers returned.</p>
        <p>This may be due to API rate limits. Please wait a minute and try again.</p>
    `;
    return;
}

            data.forEach(paper => {
                const div = document.createElement("div");
                div.className = "paper";

                let pdfLink = "";
                if (paper.openAccessPdf && paper.openAccessPdf.url) {
                    pdfLink = `<a href="${paper.openAccessPdf.url}" target="_blank">PDF</a>`;
                }

                div.innerHTML = `
                    <h3>${paper.title}</h3>
                    <p><b>Year:</b> ${paper.year || "N/A"}</p>
                    ${pdfLink}
                `;

                resultsDiv.appendChild(div);
            });
        })
        .catch(err => {
            loading.style.display = "none";
            resultsDiv.innerHTML = "Error fetching results";
        });
}

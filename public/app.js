document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("searchInput");
    const searchBtn = document.getElementById("searchBtn");
    const resultsContainer = document.getElementById("resultsContainer");
    const statsBar = document.getElementById("statsBar");
    const hitCount = document.getElementById("hitCount");
    const latencyInfo = document.getElementById("latencyInfo");
    const header = document.querySelector("header");

    const performSearch = async () => {
        const query = searchInput.value.trim();
        if (!query) return;

        header.classList.add("searched");
        resultsContainer.innerHTML = "<p style='text-align:center; color:var(--text-secondary)'>Searching...</p>";
        statsBar.style.display = "none";

        const startTime = performance.now();

        try {
            const response = await fetch("/search", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query, limit: 15 })
            });
            const data = await response.json();
            const endTime = performance.now();
            
            const latency = (endTime - startTime).toFixed(0);
            renderResults(data, latency);
        } catch (error) {
            resultsContainer.innerHTML = `<p style='text-align:center; color:red'>Error: ${error.message}</p>`;
        }
    };

    const renderResults = (data, latency) => {
        resultsContainer.innerHTML = "";
        statsBar.style.display = "flex";
        hitCount.textContent = `${data.hits} result${data.hits !== 1 ? 's' : ''} found`;
        latencyInfo.textContent = `Returned in ${latency}ms`;

        if (data.hits === 0) {
            resultsContainer.innerHTML = "<p style='text-align:center; color:var(--text-secondary)'>No documents match your query.</p>";
            return;
        }

        data.results.forEach(res => {
            const card = document.createElement("div");
            card.className = "result-card";

            const highlightedContent = res.content.replace(/\[\[(.*?)\]\]/g, '<span class="highlight">$1</span>');

            let metaTags = "";
            if (res.metadata && Object.keys(res.metadata).length > 0) {
                metaTags = `<div class="result-meta">` + 
                    Object.entries(res.metadata).map(([k, v]) => `<span class="meta-tag">${k}: ${v}</span>`).join("") +
                `</div>`;
            }

            card.innerHTML = `
                <div class="result-header">
                    <span class="result-id">Doc ID: ${res.id}</span>
                    <span class="result-score">Score: ${res.score.toFixed(4)}</span>
                </div>
                <div class="result-content">${highlightedContent}</div>
                ${metaTags}
            `;
            resultsContainer.appendChild(card);
        });
    };

    searchBtn.addEventListener("click", performSearch);
    searchInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") performSearch();
    });
});

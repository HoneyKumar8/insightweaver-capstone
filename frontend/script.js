// frontend/script.js
// Use relative API paths so it works both locally and when deployed
const API_BASE = "";

let chartRef = null;

// ---------- Load Summary ----------
async function loadSummary() {
    try {
        const res = await fetch(`${API_BASE}/summary`);
        const data = await res.json();
        document.getElementById("summaryBox").textContent = JSON.stringify(data, null, 4);
        await loadInsights();
    } catch (err) {
        document.getElementById("summaryBox").textContent = "Error loading summary: " + err;
    }
}

// ---------- Product Chart ----------
async function loadProductChart() {
    try {
        const res = await fetch(`${API_BASE}/by-product`);
        const data = await res.json();
        const labels = data.map(item => item.Product);
        const values = data.map(item => item.Sales);
        drawChart(labels, values, "Sales by Product");
    } catch (err) {
        document.getElementById("queryAnswer").textContent = "Chart error: " + err;
    }
}

// ---------- Region Chart ----------
async function loadRegionChart() {
    try {
        const res = await fetch(`${API_BASE}/by-region`);
        const data = await res.json();
        const labels = data.map(item => item.Region);
        const values = data.map(item => item.Sales);
        drawChart(labels, values, "Sales by Region");
    } catch (err) {
        document.getElementById("queryAnswer").textContent = "Chart error: " + err;
    }
}

// ---------- Draw Chart ----------
function drawChart(labels, values, titleText) {
    const ctx = document.getElementById("chartCanvas").getContext("2d");
    if (chartRef !== null) chartRef.destroy();

    chartRef = new Chart(ctx, {
        type: "bar",
        data: { labels: labels, datasets: [{ label: titleText, data: values }] },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true, position: "top" },
            },
            scales: {
                y: {
                    ticks: {
                        callback: function (value) { return value.toLocaleString(); }
                    }
                }
            }
        }
    });
}

// ---------- Insights ----------
async function loadInsights() {
    try {
        const res = await fetch(`${API_BASE}/insights`);
        const data = await res.json();
        const list = data.insights || [];
        const container = document.getElementById("insightsList");
        if (list.length === 0) {
            container.innerHTML = "<em>No interesting insights found.</em>";
            return;
        }
        const html = "<ul>" + list.map(s => `<li>${s}</li>`).join("") + "</ul>";
        container.innerHTML = html;
        return data.structured || {};
    } catch (err) {
        document.getElementById("insightsList").textContent = "Error loading insights: " + err;
    }
}

// ---------- Query UI (robust) ----------
async function sendQuery() {
    const q = document.getElementById("queryInput").value.trim();
    const out = document.getElementById("queryAnswer");
    if (!q) { out.textContent = "Please type a question."; return; }
    out.textContent = "Thinking...";
    try {
        const res = await fetch(`${API_BASE}/query?q=${encodeURIComponent(q)}`, { method: "GET" });
        const contentType = res.headers.get("content-type") || "";
        if (!res.ok || !contentType.includes("application/json")) {
            const text = await res.text();
            out.innerHTML = `<strong>Server returned an error or HTML:</strong><pre>${escapeHtml(text)}</pre>`;
            return;
        }
        const data = await res.json();
        if (data.error) { out.textContent = "Error: " + data.error; return; }
        if (data.insights) {
            out.innerHTML = "<strong>Insights:</strong><br>" + data.insights.map(s => `<div>• ${s}</div>`).join("");
            return;
        }
        out.textContent = data.answer || JSON.stringify(data);
    } catch (err) {
        out.textContent = "Network or server error: " + err;
    }
}

function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// ---------- Forecast ----------
async function loadForecast(monthsAhead = 1) {
    const out = document.getElementById("queryAnswer");
    out.textContent = "Calculating forecast...";
    try {
        const res = await fetch(`${API_BASE}/forecast?months_ahead=${monthsAhead}`);
        const contentType = res.headers.get("content-type") || "";
        if (!res.ok || !contentType.includes("application/json")) {
            const text = await res.text();
            out.innerHTML = `<strong>Server error:</strong><pre>${escapeHtml(text)}</pre>`;
            return;
        }
        const data = await res.json();
        if (data.error) { out.textContent = "Forecast error: " + data.error; return; }
        const predicted = Math.round(data.forecast.predicted_sales);
        const slope = data.forecast.model.slope.toFixed(2);
        const intercept = data.forecast.model.intercept.toFixed(2);
        out.innerHTML = `<strong>Forecast:</strong> Predicted sales for next month: <strong>${predicted.toLocaleString()}</strong><br><small>Model slope=${slope}, intercept=${intercept}</small>`;

        if (chartRef) {
            const labels = chartRef.data.labels.slice();
            const values = chartRef.data.datasets[0].data.slice();
            labels.push("Next");
            values.push(predicted);
            drawChart(labels, values, chartRef.data.datasets[0].label + " (incl. forecast)");
        }
    } catch (err) {
        out.textContent = "Forecast fetch error: " + err;
    }
}

// Auto-run on load
window.onload = function () {
    loadProductChart();
    loadInsights();
    const qi = document.getElementById("queryInput"); if (qi) qi.focus();
};

const API_BASE = "http://127.0.0.1:5000";

let chartRef = null;

// ---------- Load Summary ----------
async function loadSummary() {
    const res = await fetch(`${API_BASE}/summary`);
    const data = await res.json();
    document.getElementById("summaryBox").textContent = JSON.stringify(data, null, 4);
    // load insights as well
    await loadInsights();
}


// ---------- Product Chart ----------
async function loadProductChart() {
    const res = await fetch(`${API_BASE}/by-product`);
    const data = await res.json();

    const labels = data.map(item => item.Product);
    const values = data.map(item => item.Sales);

    drawChart(labels, values, "Sales by Product");
}

// ---------- Region Chart ----------
async function loadRegionChart() {
    const res = await fetch(`${API_BASE}/by-region`);
    const data = await res.json();

    const labels = data.map(item => item.Region);
    const values = data.map(item => item.Sales);

    drawChart(labels, values, "Sales by Region");
}

// ---------- Draw Chart (Reusable) ----------
function drawChart(labels, values, titleText) {
    const ctx = document.getElementById("chartCanvas").getContext("2d");

    if (chartRef !== null) {
        chartRef.destroy();
    }

    chartRef = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: titleText,
                data: values
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true, position: 'top' },
                title: { display: false }
            },
            scales: {
                y: {
                    ticks: {
                        // show thousands separators
                        callback: function(value) {
                            return value.toLocaleString();
                        }
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
        // Render as bullet list
        const html = "<ul>" + list.map(s => `<li>${s}</li>`).join("") + "</ul>";
        container.innerHTML = html;
        // Optionally return structured for debugging
        return data.structured || {};
    } catch (err) {
        document.getElementById("insightsList").textContent = "Error loading insights: " + err;
    }
}

// ---------- Query UI ----------
// ---------- Query UI (robust) ----------
async function sendQuery() {
    const q = document.getElementById("queryInput").value.trim();
    const out = document.getElementById("queryAnswer");
    if (!q) {
        out.textContent = "Please type a question.";
        return;
    }
    out.textContent = "Thinking...";
    try {
        const res = await fetch(`${API_BASE}/query?q=${encodeURIComponent(q)}`, { method: "GET" });

        // If server returned non-OK (status 4xx/5xx) or content-type isn't JSON, show the text
        const contentType = res.headers.get("content-type") || "";
        if (!res.ok || !contentType.includes("application/json")) {
            const text = await res.text();
            out.innerHTML = `<strong>Server returned an error or HTML:</strong><pre style="white-space:pre-wrap; color:#fdd;">${escapeHtml(text)}</pre>`;
            return;
        }

        const data = await res.json();
        if (data.error) {
            out.textContent = "Error: " + data.error;
            return;
        }
        if (data.insights) {
            out.innerHTML = "<strong>Insights:</strong><br>" + data.insights.map(s => `<div>• ${s}</div>`).join("");
            return;
        }
        out.textContent = data.answer || JSON.stringify(data);
    } catch (err) {
        out.textContent = "Network or server error: " + err;
    }
}

// small helper to safely render server HTML as text
function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;")
              .replace(/"/g, "&quot;")
              .replace(/'/g, "&#039;");
}

// ---------- Forecast ----------
async function loadForecast(monthsAhead = 1) {
    const out = document.getElementById("queryAnswer"); // reuse area for quick display
    out.textContent = "Calculating forecast...";
    try {
        const res = await fetch(`${API_BASE}/forecast?months_ahead=${monthsAhead}`);

        const contentType = res.headers.get("content-type") || "";
        if (!res.ok || !contentType.includes("application/json")) {
            const text = await res.text();
            out.textContent = "Forecast error (non-JSON response): " + text.slice(0, 200) + "...";
            return;
        }

        const data = await res.json();
        if (data.error) {
            out.textContent = "Forecast error: " + data.error;
            return;
        }
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


window.onload = function() {
    loadProductChart();
    loadInsights();
    const qi = document.getElementById("queryInput");
    if (qi) qi.focus();
};

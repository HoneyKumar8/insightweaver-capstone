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


// at bottom of script.js
window.onload = function() {
    loadProductChart();
    loadInsights();
};

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

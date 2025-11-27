const API_BASE = "http://127.0.0.1:5000";

let chartRef = null;

// ---------- Load Summary ----------
async function loadSummary() {
    const res = await fetch(`${API_BASE}/summary`);
    const data = await res.json();
    document.getElementById("summaryBox").textContent = JSON.stringify(data, null, 4);
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
        }
    });
}

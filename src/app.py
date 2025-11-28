# src/app.py
import os
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

# Import from package (works under gunicorn src.app:app)
from src.data_processing import (
    load_data,
    clean_data,
    summary_stats,
    sales_by_product,
    sales_by_region,
    generate_insights,
    handle_query,
    generate_forecast,
)

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)

# Load and cache data on startup (simple approach)
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sales_data.csv")
df = clean_data(load_data(DATA_PATH))

# Serve index.html at root
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok", "rows": len(df)})

@app.route("/summary")
def summary():
    s = summary_stats(df)
    return jsonify(s)

@app.route("/by-product")
def by_product():
    return jsonify(sales_by_product(df))

@app.route("/by-region")
def by_region():
    return jsonify(sales_by_region(df))

@app.route("/insights")
def insights():
    return jsonify(generate_insights(df))

@app.route("/query")
def query():
    q = request.args.get("q", "")
    if not q:
        return jsonify({"error": "Missing query parameter 'q'."}), 400
    if q.strip().lower() == "insights":
        return jsonify(generate_insights(df))
    ans = handle_query(df, q)
    return jsonify(ans)

@app.route("/forecast")
def forecast():
    months_ahead = int(request.args.get("months_ahead", 1))
    result = generate_forecast(df, months_ahead=months_ahead)
    return jsonify(result)

if __name__ == "__main__":
    # Run as module: python -m src.app (recommended). This block still lets you do python -m src.app
    app.run(host="127.0.0.1", port=5000, debug=True)

# src/app.py
import os
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from data_processing import (
    load_data,
    clean_data,
    summary_stats,
    sales_by_product,
    sales_by_region,
    generate_insights,
    generate_forecast,   # <-- add this
)

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)

# Load and cache data on startup
df = clean_data(load_data())

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
    """
    Returns:
      {
        "insights": ["sentence1", "sentence2", ...],
        "structured": {
            "monthly_totals": [...],
            "by_product": [...],
            "by_region": [...]
        }
      }
    """
    return jsonify(generate_insights(df))

@app.route("/query")
def query():
    """
    Simple GET query endpoint:
      /query?q=Which%20product%20sold%20the%20most%3F
    """
    q = request.args.get("q", "")
    if not q:
        return jsonify({"error": "Missing query parameter 'q'."}), 400
    result = generate_insights(df) if q.strip().lower() == "insights" else None
    if result:
        # return insights if user typed "insights"
        return jsonify(result)
    # use the rule-based handler
    from data_processing import handle_query
    ans = handle_query(df, q)
    return jsonify(ans)

@app.route("/forecast")
def forecast():
    """
    Returns a simple linear forecast for next month:
      /forecast  -> default months_ahead=1
      /forecast?months_ahead=2
    """
    months_ahead = int(request.args.get("months_ahead", 1))
    result = generate_forecast(df, months_ahead=months_ahead)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

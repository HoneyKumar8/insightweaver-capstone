# src/app.py
from flask import Flask, jsonify
from data_processing import load_data, clean_data, summary_stats, sales_by_product, sales_by_region

app = Flask(__name__)

# Load and cache data on startup (simple approach)
df = clean_data(load_data())

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

if __name__ == "__main__":
    # For local dev only. Do NOT use this in production.
    app.run(host="127.0.0.1", port=5000, debug=True)

# src/data_processing.py
import os
import pandas as pd
import numpy as np
from typing import Dict

# Resolve data path relative to package. When calling load_data you can pass an explicit path.
DEFAULT_DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sales_data.csv")
)

def load_data(path: str = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Load CSV into a pandas DataFrame."""
    df = pd.read_csv(path)
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning: drop empty rows, strip strings, convert Sales to numeric."""
    df = df.dropna(how="all")
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()
    # Make sure Sales column exists
    if "Sales" not in df.columns:
        raise ValueError("Dataset must include a 'Sales' column.")
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df = df.dropna(subset=["Sales"])
    df = df.reset_index(drop=True)
    return df

def summary_stats(df: pd.DataFrame) -> dict:
    total_sales = float(df["Sales"].sum())
    avg_sale = float(df["Sales"].mean())
    min_sale = float(df["Sales"].min())
    max_sale = float(df["Sales"].max())
    months = int(df["Month"].nunique()) if "Month" in df.columns else 0
    products = int(df["Product"].nunique()) if "Product" in df.columns else 0
    regions = int(df["Region"].nunique()) if "Region" in df.columns else 0

    return {
        "total_sales": total_sales,
        "average_sale": avg_sale,
        "min_sale": min_sale,
        "max_sale": max_sale,
        "months_count": months,
        "unique_products": products,
        "unique_regions": regions,
    }

def sales_by_product(df: pd.DataFrame):
    if "Product" not in df.columns:
        return []
    agg = df.groupby("Product", as_index=False)["Sales"].sum()
    return agg.sort_values("Sales", ascending=False).to_dict(orient="records")

def sales_by_region(df: pd.DataFrame):
    if "Region" not in df.columns:
        return []
    agg = df.groupby("Region", as_index=False)["Sales"].sum()
    return agg.sort_values("Sales", ascending=False).to_dict(orient="records")

# ---- insights helpers ----
def monthly_totals(df: pd.DataFrame) -> pd.DataFrame:
    if "Month" not in df.columns:
        return pd.DataFrame(columns=["Month", "Sales"])
    month_order = list(df["Month"].astype(str).unique())
    agg = df.groupby("Month", as_index=False)["Sales"].sum()
    agg["Month"] = pd.Categorical(agg["Month"], categories=month_order, ordered=True)
    agg = agg.sort_values("Month")
    return agg.reset_index(drop=True)

def top_product_insight(df: pd.DataFrame) -> str:
    agg = df.groupby("Product", as_index=False)["Sales"].sum()
    agg = agg.sort_values("Sales", ascending=False).reset_index(drop=True)
    top = agg.iloc[0]
    total = agg["Sales"].sum()
    perc = (top["Sales"] / total) * 100 if total else 0
    return f"Top product: {top['Product']} with {int(top['Sales']):,} sales ({perc:.1f}% of total)."

def top_region_insight(df: pd.DataFrame) -> str:
    agg = df.groupby("Region", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False).reset_index(drop=True)
    top = agg.iloc[0]
    return f"Top region: {top['Region']} with {int(top['Sales']):,} sales."

def month_over_month_insights(df: pd.DataFrame, top_n=3) -> list:
    m = monthly_totals(df)
    if m.empty:
        return []
    m["pct_change"] = m["Sales"].pct_change() * 100
    changes = m.dropna(subset=["pct_change"]).copy()
    increases = changes.sort_values("pct_change", ascending=False).head(top_n)
    out = []
    for _, row in increases.iterrows():
        out.append(f"Month-over-month change: {row['Month']} changed by {row['pct_change']:.1f}% (total {int(row['Sales']):,}).")
    return out

def anomaly_insights(df: pd.DataFrame, z_thresh=1.5) -> list:
    m = monthly_totals(df)
    if m.empty:
        return []
    sales = m["Sales"].astype(float)
    mean = sales.mean()
    std = sales.std(ddof=0) if len(sales) > 1 else 0.0
    if std == 0:
        return []
    z_scores = (sales - mean) / std
    out = []
    for idx, z in enumerate(z_scores):
        if abs(z) > z_thresh:
            month = m.loc[idx, "Month"]
            month_sales = int(m.loc[idx, "Sales"])
            out.append(f"Anomaly detected: {month} had sales {month_sales:,} (z={z:.2f}).")
    return out

def generate_insights(df: pd.DataFrame, max_insights=6) -> dict:
    insights = []
    try:
        insights.append(top_product_insight(df))
        insights.append(top_region_insight(df))
    except Exception:
        pass
    insights.extend(month_over_month_insights(df, top_n=2))
    insights.extend(anomaly_insights(df, z_thresh=1.5))
    insights = insights[:max_insights]
    structured = {
        "monthly_totals": monthly_totals(df).to_dict(orient="records"),
        "by_product": sales_by_product(df),
        "by_region": sales_by_region(df),
    }
    return {"insights": insights, "structured": structured}

# ---- query handler ----
def handle_query(df: pd.DataFrame, query: str) -> Dict:
    q = (query or "").strip().lower()
    if q == "":
        return {"answer": "Please ask a question about the data (example: 'Which product sold the most?')."}
    if "total" in q and "sale" in q:
        total = int(df["Sales"].sum())
        return {"answer": f"Total sales: {total:,}.", "details": {"total_sales": total}}
    if "product" in q and ("top" in q or "most" in q or "best" in q or "largest" in q):
        agg = df.groupby("Product", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
        top = agg.iloc[0]
        return {"answer": f"Top product is {top['Product']} with {int(top['Sales']):,} sales.", "details": {"product": top["Product"], "sales": int(top["Sales"])}}
    if "region" in q and ("top" in q or "most" in q or "largest" in q):
        agg = df.groupby("Region", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
        top = agg.iloc[0]
        return {"answer": f"Top region is {top['Region']} with {int(top['Sales']):,} sales.", "details": {"region": top["Region"], "sales": int(top["Sales"])}}
    if ("month" in q and ("high" in q or "most" in q or "highest" in q or "top" in q)):
        m = monthly_totals(df).sort_values("Sales", ascending=False).reset_index(drop=True)
        top = m.iloc[0]
        return {"answer": f"Highest-sales month is {top['Month']} with {int(top['Sales']):,} sales.", "details": {"month": top["Month"], "sales": int(top["Sales"])}}
    if "growth" in q or "increase" in q or ("month" in q and "change" in q):
        m = monthly_totals(df)
        m["pct_change"] = m["Sales"].pct_change() * 100
        changes = m.dropna(subset=["pct_change"]).copy()
        if len(changes) == 0:
            return {"answer": "No month-over-month data available to compute growth."}
        top = changes.sort_values("pct_change", ascending=False).iloc[0]
        return {"answer": f"Biggest month-over-month increase: {top['Month']} with {top['pct_change']:.1f}% (total {int(top['Sales']):,}).", "details": {"month": top["Month"], "pct_change": float(top["pct_change"]), "sales": int(top["Sales"])}}
    if "share" in q or ("what" in q and "percent" in q and "product" in q):
        agg = df.groupby("Product", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
        total = agg["Sales"].sum()
        shares = []
        for _, r in agg.iterrows():
            shares.append({"product": r["Product"], "sales": int(r["Sales"]), "pct": float((r["Sales"]/total) * 100)})
        return {"answer": "Product share computed.", "details": {"shares": shares}}
    return {"answer": "Sorry — I couldn't understand that. Try: 'top product', 'top region', 'total sales', 'month growth'."}

# ---- forecasting ----
def generate_forecast(df: pd.DataFrame, months_ahead: int = 1) -> dict:
    m_df = monthly_totals(df)
    n = len(m_df)
    if n < 2:
        return {"error": "Not enough months to forecast (need at least 2).", "monthly_totals": m_df.to_dict(orient="records")}
    x = np.arange(n).astype(float)
    y = m_df["Sales"].astype(float).values
    slope, intercept = np.polyfit(x, y, 1)
    next_x = n + (months_ahead - 1)
    predicted = float(slope * next_x + intercept)
    return {
        "monthly_totals": m_df.to_dict(orient="records"),
        "forecast": {
            "next_month_index": int(next_x),
            "predicted_sales": predicted,
            "model": {"slope": float(slope), "intercept": float(intercept)}
        }
    }

# quick local test
if __name__ == "__main__":
    df = load_data(DEFAULT_DATA_PATH)
    df = clean_data(df)
    print("Loaded rows:", len(df))
    print("Summary:", summary_stats(df))
    print("Insights:", generate_insights(df))

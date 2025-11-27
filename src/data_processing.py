# src/data_processing.py
import pandas as pd
import numpy as np

DATA_PATH = "data/sales_data.csv"

def load_data(path=DATA_PATH):
    """Load CSV into a pandas DataFrame."""
    df = pd.read_csv(path)
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Simple cleaning:
       - drop fully empty rows
       - strip whitespace from string columns
       - convert Sales to numeric
       - reset index
    """
    df = df.dropna(how="all")
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df = df.dropna(subset=["Sales"])
    df = df.reset_index(drop=True)
    return df

def summary_stats(df: pd.DataFrame) -> dict:
    total_sales = float(df["Sales"].sum())
    avg_sale = float(df["Sales"].mean())
    min_sale = float(df["Sales"].min())
    max_sale = float(df["Sales"].max())
    months = int(df["Month"].nunique())
    products = int(df["Product"].nunique())
    regions = int(df["Region"].nunique())

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
    agg = df.groupby("Product", as_index=False)["Sales"].sum()
    return agg.sort_values("Sales", ascending=False).to_dict(orient="records")

def sales_by_region(df: pd.DataFrame):
    agg = df.groupby("Region", as_index=False)["Sales"].sum()
    return agg.sort_values("Sales", ascending=False).to_dict(orient="records")

# ---- New helpers for insights ----

def monthly_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Return dataframe with total sales per Month in calendar order found in data."""
    # Ensure Month order is preserved by first appearance in dataset
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
    """Return list of strings describing largest month-over-month increases."""
    m = monthly_totals(df)
    # compute pct change
    m["pct_change"] = m["Sales"].pct_change() * 100
    # drop NaN (first entry)
    changes = m.dropna(subset=["pct_change"]).copy()
    # get top increases
    increases = changes.sort_values("pct_change", ascending=False).head(top_n)
    out = []
    for _, row in increases.iterrows():
        out.append(f"Month-over-month change: {row['Month']} changed by {row['pct_change']:.1f}% (total {int(row['Sales']):,}).")
    return out

def anomaly_insights(df: pd.DataFrame, z_thresh=1.5) -> list:
    """Simple anomaly detection on monthly totals using z-score.
       Returns sentences for months with |z| > z_thresh.
    """
    m = monthly_totals(df)
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
    """Return a structured set of insights (both sentences and some supporting numbers)."""
    insights = []
    # Top product & region
    insights.append(top_product_insight(df))
    insights.append(top_region_insight(df))

    # Month over month growth notes
    mom = month_over_month_insights(df, top_n=2)
    insights.extend(mom)

    # Anomalies
    anoms = anomaly_insights(df, z_thresh=1.5)
    insights.extend(anoms)

    # Trim to max_insights
    insights = insights[:max_insights]

    # Also include some structured values
    structured = {
        "monthly_totals": monthly_totals(df).to_dict(orient="records"),
        "by_product": sales_by_product(df),
        "by_region": sales_by_region(df),
    }
    return {"insights": insights, "structured": structured}

# quick local test when run directly
if __name__ == "__main__":
    df = load_data()
    df = clean_data(df)
    print("Loaded rows:", len(df))
    print("Summary:", summary_stats(df))
    print("By product:", sales_by_product(df))
    print("Insights:", generate_insights(df))

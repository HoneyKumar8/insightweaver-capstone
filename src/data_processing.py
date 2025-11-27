# src/data_processing.py
import pandas as pd

DATA_PATH = "data/sales_data.csv"

def load_data(path=DATA_PATH):
    """Load CSV into a pandas DataFrame."""
    df = pd.read_csv(path)
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Simple cleaning:
       - strip whitespace from string columns
       - convert Sales to numeric (if not)
       - drop completely empty rows
    """
    # Drop rows that are fully empty
    df = df.dropna(how="all")

    # Strip whitespace on string columns
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()

    # Ensure Sales is numeric
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")

    # Optionally drop rows where Sales is NaN
    df = df.dropna(subset=["Sales"])

    # Reset index
    df = df.reset_index(drop=True)
    return df

def summary_stats(df: pd.DataFrame) -> dict:
    """Return high-level summary statistics as a Python dict."""
    total_sales = float(df["Sales"].sum())
    avg_sale = float(df["Sales"].mean())
    min_sale = float(df["Sales"].min())
    max_sale = float(df["Sales"].max())
    months = df["Month"].nunique()
    products = df["Product"].nunique()
    regions = df["Region"].nunique()

    return {
        "total_sales": total_sales,
        "average_sale": avg_sale,
        "min_sale": min_sale,
        "max_sale": max_sale,
        "months_count": int(months),
        "unique_products": int(products),
        "unique_regions": int(regions),
    }

def sales_by_product(df: pd.DataFrame) -> dict:
    """Aggregate sales by product -> returns mapping product -> sum."""
    agg = df.groupby("Product", as_index=False)["Sales"].sum()
    # Convert to list of dicts for JSON friendliness
    return agg.sort_values("Sales", ascending=False).to_dict(orient="records")

def sales_by_region(df: pd.DataFrame) -> dict:
    """Aggregate sales by region -> returns mapping region -> sum."""
    agg = df.groupby("Region", as_index=False)["Sales"].sum()
    return agg.sort_values("Sales", ascending=False).to_dict(orient="records")

# quick local test when run directly
if __name__ == "__main__":
    df = load_data()
    df = clean_data(df)
    print("Loaded rows:", len(df))
    print("Summary:", summary_stats(df))
    print("By product:", sales_by_product(df))

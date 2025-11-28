# tests/test_data_processing.py
import pandas as pd
from src import data_processing as dp

# small synthetic dataset to validate logic
SAMPLE = pd.DataFrame([
    {"Month": "Jan", "Product": "A", "Region": "North", "Sales": 100},
    {"Month": "Feb", "Product": "A", "Region": "North", "Sales": 120},
    {"Month": "Mar", "Product": "B", "Region": "South", "Sales": 80},
    {"Month": "Mar", "Product": "A", "Region": "North", "Sales": 90},
])

def test_summary_stats():
    df = dp.clean_data(SAMPLE.copy())
    s = dp.summary_stats(df)
    assert s["total_sales"] == 390
    assert s["unique_products"] == 2
    assert s["unique_regions"] == 2

def test_sales_by_product():
    df = dp.clean_data(SAMPLE.copy())
    byp = dp.sales_by_product(df)
    # check highest product is 'A'
    assert byp[0]["Product"] == "A"

def test_generate_forecast_minimum():
    # With 3 months present, forecast should return a forecast dict
    df = dp.clean_data(SAMPLE.copy())
    out = dp.generate_forecast(df, months_ahead=1)
    assert "forecast" in out
    assert "predicted_sales" in out["forecast"]
